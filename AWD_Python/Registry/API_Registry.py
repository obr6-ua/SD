from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from pymongo import MongoClient
import hashlib

app = Flask(__name__)
CORS(app)

@app.route('/register', methods=['POST'])
def registrarApi():
    data = request.json
    drone_id = data.get('id')
    # Ciframos el id y lo usamos como token para mandar
    token = hashlib.sha256(drone_id.encode()).hexdigest()
    token = token[10:25]

    hora = datetime.now() + timedelta(seconds=20)
    #Dron
    nuevo_dron = {"id": drone_id, "alias" : drone_id, "token" : token, "hora" : hora}
    #Inserto el nuevo dron en db
    client = MongoClient("mongodb://192.168.23.1:27017")
    db = client['drones_db']
    coleccion = db['drones']
    coleccion.insert_one(nuevo_dron)

    return jsonify({"message": "Dron registrado con éxito", "token": token}), 200

def main():
    SERVER = '0.0.0.0' 
    PORT = 5001 

    app.run(port=PORT, host=SERVER)

if __name__ == '__main__':
    main()