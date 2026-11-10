# Estigia · Analizador de mediciones

Esta versión sustituye la animación sintética de Lorenz como herramienta principal por un analizador local de **mediciones que proporciona el usuario**. Ya no genera la serie analizada a partir de una simulación.

## Ejecutar

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000. El servidor escucha solo en la computadora local. No introduzcas datos sensibles en un servidor público.

También se puede iniciar con `python simulation.py` o `python "Código.mat.py"`; ambos nombres antiguos ahora abren la nueva aplicación, no vuelven a ejecutar la simulación anterior.

## Qué analiza

- Serie temporal numérica observada: cantidad, mínimo, máximo, media, desviación estándar y tendencia lineal por muestra.
- Error RMSE del ajuste lineal y extrapolación descriptiva para un horizonte configurable.
- Distancia actual a un umbral y cruce estimado si la tendencia lineal lo alcanza.
- Comparación opcional entrada/salida: brecha con signo, brecha absoluta, brecha relativa cuando la entrada no es cero y diferencia inversa.
- Panel SOFI opcional con las fórmulas numéricas suministradas: banda, regla de frecuencia inversa, amplitud, energía, frecuencia cardíaca, período y la fórmula de coherencia SOFI.
- Gráfico de la serie y control de decimales de presentación (0–15).

El número de decimales solo controla el redondeo que se muestra; no aumenta la exactitud instrumental ni la precisión de los datos originales. La extrapolación lineal no es una probabilidad calibrada. El análisis SOFI preserva las fórmulas aritméticas, pero no interpreta sus salidas como estados inconscientes ni como diagnóstico médico: esas conclusiones no se desprenden matemáticamente de las fórmulas.

## API local

`POST /api/analizar` acepta JSON. Ejemplo:

```json
{
  "serie": [1.2, 1.4, 1.9, 2.1, 2.8, 3.0],
  "unidad": "unidades",
  "decimales": 8,
  "horizonte": 3,
  "umbral": 5,
  "sentido_umbral": "arriba",
  "entrada": 2.4,
  "salida": 3.1,
  "sofi": {
    "frecuenciaActual": 12.3,
    "ritmoCardiaco": 72,
    "spo2": 97,
    "irritabilidad": 30
  }
}
```

Los campos `entrada` y `salida` deben aparecer juntos. `sofi` es opcional. Para mediciones reales, introduce valores obtenidos por instrumentos/sistemas apropiados, junto con unidades y marcas de tiempo coherentes.

## Sobre AUREC y predicciones

La información compartida para AUREC era un enlace HTML temporal, no el código fuente legible del analizador; por tanto, no se inventan ni se atribuyen fórmulas de AUREC a esta herramienta. La app queda preparada para ampliarse cuando el código y sus definiciones de métricas estén disponibles. Actualmente no calcula probabilidades de colapso/eventos ni garantiza que algo sucederá. Para ello se necesitan eventos definidos, suficientes observaciones etiquetadas y evaluación retrospectiva/fuera de muestra.

## Pruebas

```bash
python -m unittest discover -s tests -v
```
