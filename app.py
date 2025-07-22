from flask import Flask, request, jsonify
from flask_cors import CORS 
import joblib
import logging
import pandas as pd

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

try:
    rules: pd.DataFrame = joblib.load('reglas_asociacion.pkl')
    logging.info("Modelo de reglas de asociación cargado exitosamente.")
except Exception as e:
    logging.error(f"Error al cargar el modelo: {e}")
    rules = pd.DataFrame()

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>API de Recomendación</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                color: #333;
                display: flex;
                justify-content:start;
                align-items: start;
                height: 100vh;
                margintop: 50px;
                margin-left: 50px;
            }
            .box {
                background: #fff;
                padding: 20px 30px;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                text-align: center;
            }
            code {
                background-color: #eee;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: monospace;
                color: #c0392b;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>API de Recomendación</h2>
            <p>Está corriendo correctamente</p>
            <p>Haz POST a <code>/recomendar</code>
        </div>
    </body>
    </html>
    """

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

        recomendaciones -= productos_set 
        recomendaciones = set(r.strip() for r in recomendaciones) 

        return jsonify(sorted(recomendaciones))

    except Exception as e:
        logging.error(f"Error en la ruta /recomendar: {e}")
        return jsonify({"error": "Ocurrió un error al procesar la solicitud."}), 500

if __name__ == '__main__':
    app.run(debug=True)
