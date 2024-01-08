from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

def leer_mapa_desde_db(self):
    try:
        documento_mapa = self.bd.mapa.find_one({'_id': 'ID_MAPA'})
        if documento_mapa and 'mapa' in documento_mapa:
            return documento_mapa['mapa']
        else:
            print("No se encontró el mapa en la base de datos.")
            return None
    except Exception as ex:
        print(f"Error al leer el mapa desde la base de datos: {ex}")
        return None

@app.route('/mapa', methods=["GET"])
@cross_origin()
def getMap():
    try:
        mapa_dict = leer_mapa_desde_db()
        if mapa_dict:
            return jsonify(mapa_dict)
        else:
            return jsonify({"error": "Mapa no disponible"}), 404
    except Exception as ex:
        print(ex)
        return jsonify({"error": "Error interno"}), 500

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return "<h1>La página que intentas acceder no existe ...</h1>"

def main():
    SERVER = '0.0.0.0' 
    PORT = 5000  

    app.run(port=PORT, host=SERVER)

if __name__ == '__main__':
    main()