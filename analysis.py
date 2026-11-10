"""Descriptive analysis for user-provided numeric measurements and text."""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any

import numpy as np

BANDS = {
    "Delta": {"min": 0.5, "max": 3.5}, "Theta": {"min": 4.0, "max": 7.0},
    "Alpha": {"min": 8.0, "max": 13.0}, "Beta": {"min": 14.0, "max": 30.0},
    "Gamma": {"min": 30.0, "max": 100.0},
}
NUMBER_RE = re.compile(r"(?<![\w.])[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?(?![\w.])")
WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def _finite_number(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{name}' debe ser un número.") from None
    if not math.isfinite(number):
        raise ValueError(f"'{name}' debe ser finito.")
    return number


def _extract_series(payload: dict[str, Any]) -> tuple[list[float], str | None]:
    if isinstance(payload.get("serie"), list):
        return [_finite_number(v, f"serie[{i}]") for i, v in enumerate(payload["serie"])], payload.get("texto")
    text = payload.get("texto", payload.get("contenido"))
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Pega texto o carga un archivo con al menos dos mediciones numéricas.")
    if len(text) > 2_000_000:
        raise ValueError("El texto supera el límite de 2 MB.")
    stripped = text.strip()
    if stripped.startswith(("[", "{")):
        try:
            obj = json.loads(stripped)
            if isinstance(obj, list):
                values = obj
            elif isinstance(obj, dict):
                values = obj.get("serie", obj.get("values", obj.get("data")))
                if not isinstance(values, list):
                    raise ValueError("El JSON debe contener una lista en serie, values o data.")
            else:
                raise ValueError("El JSON debe ser una lista o un objeto con una lista numérica.")
            return [_finite_number(v, f"dato[{i}]") for i, v in enumerate(values)], text
        except json.JSONDecodeError:
            # Plain text may start with a bracket; fall through to numeric extraction.
            pass
    values = []
    for match in NUMBER_RE.finditer(text):
        token = match.group().replace(",", ".")
        try:
            number = float(token)
        except ValueError:
            continue
        if math.isfinite(number):
            values.append(number)
    if len(values) < 2:
        raise ValueError("No encontré al menos dos números en el texto. Pega una serie o carga TXT, CSV o JSON.")
    return values, text


def identify_band(hz: float) -> str:
    return next((name for name, limits in BANDS.items() if limits["min"] <= hz <= limits["max"]), "Fuera de bandas configuradas")


def analyze_sofi(biometric: dict[str, Any], decimals: int = 6) -> dict[str, Any]:
    hz = _finite_number(biometric.get("frecuenciaActual", 12.3), "frecuenciaActual")
    bpm = _finite_number(biometric.get("ritmoCardiaco", 72), "ritmoCardiaco")
    spo2 = _finite_number(biometric.get("spo2", 97), "spo2")
    irritability = _finite_number(biometric.get("irritabilidad", 30), "irritabilidad")
    if not 0.5 <= hz <= 100: raise ValueError("frecuenciaActual debe estar entre 0.5 y 100 Hz.")
    if not 20 <= bpm <= 250: raise ValueError("ritmoCardiaco debe estar entre 20 y 250 BPM.")
    if not 50 <= spo2 <= 100: raise ValueError("spo2 debe estar entre 50 y 100 %.")
    if not 0 <= irritability <= 100: raise ValueError("irritabilidad debe estar entre 0 y 100.")
    band = identify_band(hz)
    limits = BANDS.get(band)
    inverse = amplitude = energy = None
    if limits:
        width = limits["max"] - limits["min"]
        inverse = max(0.5, limits["max"] - (hz - limits["min"]))
        amplitude = max(0.0, 1 - abs(hz - (limits["min"] + limits["max"]) / 2) / width)
        energy = amplitude * inverse
    cardiac_hz = bpm / 60
    coherence = max(0.0, 1 - abs(hz - cardiac_hz * 10) / hz)
    r = lambda x: round(float(x), decimals) if x is not None else None
    return {"entrada": {"frecuencia_cerebral_hz": r(hz), "banda": band, "ritmo_cardiaco_bpm": r(bpm), "spo2_porcentaje": r(spo2), "irritabilidad_escala_0_100": r(irritability)},
            "metricas_heuristicas": {"frecuencia_inversa_regla_sofi_hz": r(inverse), "amplitud_regla_sofi": r(amplitude), "energia_regla_sofi": r(energy), "frecuencia_cardiaca_hz": r(cardiac_hz), "periodo_cardiaco_segundos": r(60 / bpm), "coherencia_formula_sofi": r(coherence)},
            "limites": "Fórmulas heurísticas suministradas; no son FFT inversa, diagnóstico ni medición validada de estados mentales."}


def _channel(values: np.ndarray, decimals: int, horizon: float) -> dict[str, Any]:
    r = lambda v: round(float(v), decimals)
    n = len(values)
    x = np.arange(n, dtype=float)
    slope, intercept = np.polyfit(x, values, 1)
    fitted = intercept + slope * x
    rmse = float(np.sqrt(np.mean((values - fitted) ** 2)))
    forecast = intercept + slope * (n - 1 + horizon)
    centered = values - values.mean()
    spectrum = np.abs(np.fft.rfft(centered))
    frequencies = np.fft.rfftfreq(n, d=1.0)
    if len(spectrum) > 1:
        spectrum[0] = 0
        peak = int(np.argmax(spectrum))
        dominant = {"ciclos_por_muestra": r(frequencies[peak]), "amplitud_fft": r(spectrum[peak]),
                    "periodo_muestras": r(1 / frequencies[peak]) if frequencies[peak] else None}
    else:
        dominant = None
    max_lag = min(n - 1, 100)
    denom = float(np.dot(centered, centered))
    autocorr = []
    for lag in range(1, max_lag + 1):
        value = float(np.dot(centered[:-lag], centered[lag:]) / denom) if denom else 0.0
        autocorr.append({"retardo_muestras": lag, "autocorrelacion": r(value)})
    return {"cantidad": n, "minimo": r(np.min(values)), "maximo": r(np.max(values)),
            "media": r(np.mean(values)), "desviacion_estandar": r(np.std(values)),
            "pendiente_por_muestra": r(slope), "direccion": "estable" if abs(slope) < 1e-12 else ("ascendente" if slope > 0 else "descendente"),
            "rmse_ajuste_lineal": r(rmse), "extrapolacion_lineal": r(forecast),
            "frecuencia_dominante": dominant, "autocorrelacion_hasta_100_retardos": autocorr,
            "serie": [r(v) for v in values]}


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    decimals = int(payload.get("decimales", 6))
    if not 0 <= decimals <= 15: raise ValueError("decimales debe estar entre 0 y 15.")
    raw, text = _extract_series(payload)
    if len(raw) < 2: raise ValueError("Se necesitan al menos dos mediciones.")
    if len(raw) > 100_000: raise ValueError("La serie no puede superar 100 000 mediciones.")
    values = np.asarray(raw, dtype=float)
    horizon = _finite_number(payload.get("horizonte", 1), "horizonte")
    if not 0 < horizon <= 1_000_000: raise ValueError("horizonte debe ser mayor que 0 y no superar 1 000 000 muestras.")
    linear = _channel(values, decimals, horizon)
    # The second path intentionally reads the same observations in reverse order.
    # This is a directional comparison, not a physical inverse or causal model.
    counterpart = _channel(values[::-1], decimals, horizon)
    result: dict[str, Any] = {
        "tipo": "analisis_paralelo_de_mediciones_observadas", "cantidad_mediciones": len(raw),
        "unidad": str(payload.get("unidad", "sin especificar"))[:40], "precision_presentacion_decimales": decimals,
        "proceso_lineal": {"metodo": "Serie en orden recibido; tendencia lineal, ajuste, FFT discreta y autocorrelación.", **linear},
        "proceso_contraparte": {"metodo": "Mismas mediciones en orden temporal inverso: comparación de dirección. No es una inversión física/causal ni la heurística SOFI.", **counterpart},
        "comparacion_procesos": {"diferencia_pendientes": round(linear["pendiente_por_muestra"] + counterpart["pendiente_por_muestra"], decimals),
                                "nota": "Al invertir exactamente el orden, la pendiente temporal debería cambiar de signo; estadísticas de distribución se mantienen."},
        "advertencia": "Descripción estadística de datos suministrados. FFT y autocorrelación requieren muestreo regular; extrapolación lineal no está calibrada como probabilidad ni garantiza eventos.",
    }
    if text is not None:
        words = [w.lower() for w in WORD_RE.findall(text)]
        frequencies = Counter(words)
        result["analisis_textual"] = {"caracteres": len(text), "palabras": len(words), "palabras_unicas": len(frequencies),
            "terminos_repetidos_mas_comunes": [{"termino": term, "apariciones": count} for term, count in frequencies.most_common(12)],
            "nota": "Resumen léxico básico; no es interpretación semántica del contenido."}
    if "entrada" in payload or "salida" in payload:
        if "entrada" not in payload or "salida" not in payload: raise ValueError("Para comparar, proporciona ambos campos: entrada y salida.")
        entry, output = _finite_number(payload["entrada"], "entrada"), _finite_number(payload["salida"], "salida")
        gap = output - entry
        result["comparacion_entrada_salida"] = {"entrada": round(entry, decimals), "salida": round(output, decimals),
            "brecha_salida_menos_entrada": round(gap, decimals), "brecha_absoluta": round(abs(gap), decimals),
            "brecha_relativa_sobre_entrada": round(abs(gap) / abs(entry), decimals) if entry else None,
            "diferencia_inversa_entrada_menos_salida": round(-gap, decimals)}
    if payload.get("umbral") is not None:
        threshold = _finite_number(payload["umbral"], "umbral")
        side = payload.get("sentido_umbral", "arriba")
        if side not in ("arriba", "abajo"): raise ValueError("sentido_umbral debe ser arriba o abajo.")
        current = values[-1]
        distance = threshold - current if side == "arriba" else current - threshold
        slope = float(np.polyfit(np.arange(len(values)), values, 1)[0])
        crossing = (threshold - current) / slope if ((side == "arriba" and slope > 0 and current < threshold) or (side == "abajo" and slope < 0 and current > threshold)) else None
        result["umbral"] = {"valor": round(threshold, decimals), "sentido": side, "distancia_actual": round(abs(float(distance)), decimals),
            "muestras_estimadas_hasta_umbral": round(crossing, decimals) if crossing is not None else None,
            "nota": "Estimación lineal descriptiva, no certeza ni probabilidad calibrada."}
    if isinstance(payload.get("sofi"), dict): result["modulo_sofi"] = analyze_sofi(payload["sofi"], decimals)
    return result
