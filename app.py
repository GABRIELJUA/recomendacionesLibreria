from flask import Flask, request, jsonify
from flask_cors import CORS  # 👈 IMPORTANTE
import joblib
import logging
import pandas as pd


app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"])  # 👈 PERMITE CORS solo desde Angular

logging.basicConfig(level=logging.INFO)

# Cargar modelo de reglas de asociación
try:
    rules: pd.DataFrame = joblib.load('reglas_asociacion.pkl')
    logging.info("Modelo de reglas de asociación cargado exitosamente.")
except Exception as e:
    logging.error(f"Error al cargar el modelo: {e}")
    rules = pd.DataFrame()  # Evita errores si carga falla

@app.route('/')
def home():
    return "API corriendo. Usa POST a /recomendar con JSON"

@app.route('/recomendar', methods=['POST'])
def recomendar():
    try:
        data = request.get_json(force=True)
        productos = data.get('productos')
        
        if not productos or not isinstance(productos, list):
            return jsonify({"error": "Se requiere una lista válida de productos."}), 400

        productos_set = set(productos)
        recomendaciones = set()

        for _, row in rules.iterrows():
            if set(row['antecedents']).issubset(productos_set):
                recomendaciones.update(set(row['consequents']))

        recomendaciones -= productos_set  # Quitar productos ya seleccionados
        recomendaciones = set(r.strip() for r in recomendaciones)  # Limpiar espacios

        return jsonify(sorted(recomendaciones))

    except Exception as e:
        logging.error(f"Error en la ruta /recomendar: {e}")
        return jsonify({"error": "Ocurrió un error al procesar la solicitud."}), 500

if __name__ == '__main__':
    app.run(debug=True)