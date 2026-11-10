# Estigia · Analizador paralelo de patrones

La herramienta recibe texto pegado o archivos TXT, CSV y JSON (límite 2 MB), extrae una serie numérica y muestra la forma de los datos. El análisis corre en dos rutas sobre la misma entrada:

1. **Ruta lineal:** respeta el orden recibido y calcula estadísticas, tendencia/ajuste lineal, RMSE, extrapolación descriptiva, FFT discreta y autocorrelación.
2. **Ruta contraparte:** vuelve a procesar la serie en orden inverso y presenta las mismas medidas para comparar la dirección temporal. No es una inversión causal, una contraparte física ni una probabilidad.

También ofrece comparación entrada/salida, distancia y tiempo estimado a un umbral, resumen léxico básico del texto y el módulo SOFI opcional con las fórmulas numéricas aportadas.

## Ejecutar localmente

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000. El servicio escucha en localhost. No expongas mediciones o datos biométricos sensibles a una red pública.

## Formatos

- Texto pegado con una secuencia numérica, como `1.2, 1.4, 1.9, 2.1`.
- Archivos `.txt`, `.csv` y `.json` arrastrados al área de carga.
- JSON con una lista o con una clave `serie`, `values` o `data`.
- Se extraen hasta 100 000 valores y se aceptan archivos/textos de hasta 2 MB.

El separador decimal esperado es punto (por ejemplo, `1.25`). En CSV, evita números con coma decimal para que la coma no se confunda con separador de columnas.

## Interpretación y límites

La FFT y autocorrelación requieren datos muestreados regularmente; la frecuencia informada está en ciclos por muestra porque no se solicita una frecuencia de muestreo. El resumen textual solo cuenta palabras y repeticiones: no realiza interpretación semántica. Las fórmulas SOFI conservan su condición de heurísticas; no constituyen una FFT inversa o diagnóstico. Decimales controla redondeo de presentación, no precisión de medición. La extrapolación lineal no es una predicción validada ni una probabilidad de colapso/evento.

AUREC todavía no se integra porque no se dispone de su código fuente legible y de sus fórmulas en la conversación/repo; no se inventan sus análisis.

## Pruebas

```bash
python -m unittest discover -s tests -v
```
