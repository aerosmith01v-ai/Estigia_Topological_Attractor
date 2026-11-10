from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from analysis import analyze

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/analizar")
def api_analyze():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Envía un objeto JSON válido."}), 400
    try:
        return jsonify(analyze(payload))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "El archivo o texto supera el límite de 2 MB."}), 413


def main():
    print("Estigia — análisis paralelo de mediciones: http://127.0.0.1:5000")
    print("Servidor local; no cargues datos sensibles en un servidor público.")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
