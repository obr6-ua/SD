from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Esto permitirá las solicitudes CORS desde cualquier origen

# Datos simulados del mapa para propósitos de prueba . Tiene que ser de 20x20 y cada celda tiene que ser un string
current_map = [
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
    ["", "", "", "", "","", "", "", "", "","", "", "", "", "","", "", "", "", ""],
]

@app.route('/mapa', methods=["GET"])
def get_map():
    try:
        return jsonify(current_map)
    except Exception as ex:
        print(ex)
        return jsonify({"error": "Error interno"}), 500

@app.route('/update', methods=["POST"])
def update_map():
    global current_map
    try:
        current_map = request.json
        return jsonify({"status": "Mapa actualizado"}), 200
    except Exception as ex:
        print(ex)
        return jsonify({"error": "Error interno"}), 500

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return "<h1>La página que intentas acceder no existe ...</h1>"

def main():
    SERVER = os.getenv('IP_API_ENGINE', '0.0.0.0')
    PORT = int(os.getenv('PORT_API_ENGINE', 5000))

    app.run(port=PORT, host=SERVER)

if __name__ == '__main__':
    main()
