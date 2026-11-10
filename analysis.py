"""Analysis of observed measurements (not a synthetic Lorenz simulation)."""
from __future__ import annotations

import math
from typing import Any

import numpy as np


BANDS = {
    "Delta": {"min": 0.5, "max": 3.5, "state": "banda de referencia Delta"},
    "Theta": {"min": 4.0, "max": 7.0, "state": "banda de referencia Theta"},
    "Alpha": {"min": 8.0, "max": 13.0, "state": "banda de referencia Alpha"},
    "Beta": {"min": 14.0, "max": 30.0, "state": "banda de referencia Beta"},
    "Gamma": {"min": 30.0, "max": 100.0, "state": "banda de referencia Gamma"},
}


def _finite_number(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{name}' debe ser un número.") from None
    if not math.isfinite(number):
        raise ValueError(f"'{name}' debe ser un número finito.")
    return number


def identify_band(hz: float) -> str:
    for name, limits in BANDS.items():
        if limits["min"] <= hz <= limits["max"]:
            return name
    return "Fuera de bandas configuradas"


def analyze_sofi(biometric: dict[str, Any], decimals: int = 6) -> dict[str, Any]:
    """Compute SOFI's declared numeric heuristics; do not infer diagnoses/states."""
    hz = _finite_number(biometric.get("frecuenciaActual", 12.3), "frecuenciaActual")
    bpm = _finite_number(biometric.get("ritmoCardiaco", 72), "ritmoCardiaco")
    spo2 = _finite_number(biometric.get("spo2", 97), "spo2")
    irritability = _finite_number(biometric.get("irritabilidad", 30), "irritabilidad")
    if not 0.5 <= hz <= 100:
        raise ValueError("frecuenciaActual debe estar entre 0.5 y 100 Hz para estas bandas.")
    if not 20 <= bpm <= 250:
        raise ValueError("ritmoCardiaco debe estar entre 20 y 250 BPM.")
    if not 50 <= spo2 <= 100:
        raise ValueError("spo2 debe estar entre 50 y 100 %.")
    if not 0 <= irritability <= 100:
        raise ValueError("irritabilidad debe estar entre 0 y 100.")

    band = identify_band(hz)
    limits = BANDS.get(band)
    inverse = amplitude = energy = None
    if limits:
        fmax = limits["max"]
        inverse = max(0.5, fmax - (hz - limits["min"]))
        center = (limits["min"] + fmax) / 2
        amplitude = max(0.0, 1 - abs(hz - center) / (fmax - limits["min"]))
        energy = amplitude * inverse
    cardiac_hz = bpm / 60
    coherence = max(0.0, 1 - abs(hz - cardiac_hz * 10) / hz)
    rounded = lambda v: round(v, decimals) if v is not None else None
    return {
        "entrada": {"frecuencia_cerebral_hz": rounded(hz), "banda": band,
                    "ritmo_cardiaco_bpm": rounded(bpm), "spo2_porcentaje": rounded(spo2),
                    "irritabilidad_escala_0_100": rounded(irritability)},
        "metricas_heuristicas": {
            "frecuencia_inversa_regla_sofi_hz": rounded(inverse),
            "amplitud_regla_sofi": rounded(amplitude), "energia_regla_sofi": rounded(energy),
            "frecuencia_cardiaca_hz": rounded(cardiac_hz),
            "periodo_cardiaco_segundos": rounded(60 / bpm),
            "coherencia_formula_sofi": rounded(coherence),
        },
        "limites": "Fórmulas heurísticas aportadas por SOFI; no son FFT inversa, diagnóstico ni medición validada de estados mentales.",
    }


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    """Analyze a measured numeric series and optional paired input/output values."""
    decimals = int(payload.get("decimales", 6))
    if not 0 <= decimals <= 15:
        raise ValueError("decimales debe estar entre 0 y 15.")
    raw_series = payload.get("serie")
    if not isinstance(raw_series, list) or len(raw_series) < 2:
        raise ValueError("'serie' debe contener al menos dos mediciones numéricas.")
    values = np.asarray([_finite_number(v, f"serie[{i}]") for i, v in enumerate(raw_series)], dtype=float)
    if len(values) > 100_000:
        raise ValueError("La serie no puede superar 100 000 mediciones.")

    x = np.arange(len(values), dtype=float)
    slope, intercept = np.polyfit(x, values, 1)
    horizon = _finite_number(payload.get("horizonte", 1), "horizonte")
    if not 0 < horizon <= 1_000_000:
        raise ValueError("horizonte debe ser mayor que 0 y no superar 1 000 000 muestras.")
    forecast = intercept + slope * (len(values) - 1 + horizon)
    residuals = values - (intercept + slope * x)
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    direction = "estable" if abs(slope) < 1e-12 else ("ascendente" if slope > 0 else "descendente")
    rounded = lambda v: round(float(v), decimals)

    result: dict[str, Any] = {
        "tipo": "analisis_de_mediciones_observadas",
        "cantidad_mediciones": int(len(values)),
        "unidad": str(payload.get("unidad", "sin especificar"))[:40],
        "serie": [rounded(v) for v in values],
        "estadisticas": {"ultima_medicion": rounded(values[-1]), "minimo": rounded(values.min()),
                         "maximo": rounded(values.max()), "media": rounded(values.mean()),
                         "desviacion_estandar": rounded(values.std()),
                         "tendencia_por_muestra": rounded(slope), "direccion_tendencia": direction,
                         "error_rmse_del_ajuste_lineal": rounded(rmse)},
        "extrapolacion_lineal": {"horizonte_muestras": rounded(horizon),
                                 "valor_estimado": rounded(forecast),
                                 "advertencia": "Extrapolación descriptiva, no probabilidad ni predicción validada. Su fiabilidad depende de datos y validación."},
        "precision_presentacion_decimales": decimals,
    }

    if "entrada" in payload or "salida" in payload:
        if "entrada" not in payload or "salida" not in payload:
            raise ValueError("Para comparar, proporciona ambos campos: 'entrada' y 'salida'.")
        entry = _finite_number(payload["entrada"], "entrada")
        output = _finite_number(payload["salida"], "salida")
        gap = output - entry
        result["comparacion_entrada_salida"] = {
            "entrada": rounded(entry), "salida": rounded(output),
            "brecha_salida_menos_entrada": rounded(gap),
            "brecha_absoluta": rounded(abs(gap)),
            "brecha_relativa_sobre_entrada": rounded(abs(gap) / abs(entry)) if entry else None,
            "diferencia_inversa_entrada_menos_salida": rounded(-gap),
            "nota": "La brecha relativa no se define cuando la entrada es cero.",
        }

    threshold_value = payload.get("umbral")
    if threshold_value is not None:
        threshold = _finite_number(threshold_value, "umbral")
        side = payload.get("sentido_umbral", "arriba")
        if side not in ("arriba", "abajo"):
            raise ValueError("sentido_umbral debe ser 'arriba' o 'abajo'.")
        current_gap = threshold - values[-1] if side == "arriba" else values[-1] - threshold
        projected_gap = threshold - forecast if side == "arriba" else forecast - threshold
        crossing_samples = None
        if (side == "arriba" and slope > 0 and values[-1] < threshold) or (side == "abajo" and slope < 0 and values[-1] > threshold):
            crossing_samples = max(0.0, (threshold - values[-1]) / slope)
        result["umbral"] = {
            "valor": rounded(threshold), "sentido": side,
            "distancia_actual_al_umbral": rounded(abs(current_gap)),
            "estimacion_lineal_supera_umbral_en_muestras": rounded(crossing_samples) if crossing_samples is not None else None,
            "extrapolacion_lineal_cruza_umbral": bool(projected_gap <= 0),
            "nota": "Cruce estimado mediante tendencia lineal, no certeza ni probabilidad calibrada.",
        }
    if isinstance(payload.get("sofi"), dict):
        result["sofi"] = analyze_sofi(payload["sofi"], decimals)
    return result
