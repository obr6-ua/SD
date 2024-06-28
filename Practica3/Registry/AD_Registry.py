from pymongo import MongoClient
from random import randint
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import hashlib
import socket
import sys
import os
import threading

FORMAT = 'utf-8'
HEADER = 4096

# IP y puerto de la BBDD
IP_BBDD = os.getenv('IP_BBDD')
PORT_BBDD = os.getenv('PORT_BBDD')
PORT_API_REGISTRY = int(os.getenv('PORT_API_REGISTRY', 3003))

clave_encriptada = os.getenv('CLAVE_ENCRIPTADA').encode()
cipher_suite = Fernet(clave_encriptada)


def encriptar_mensaje(mensaje):
    if isinstance(mensaje, str):
        mensaje_bytes = mensaje.encode(FORMAT)
    else:
        mensaje_bytes = mensaje
    mensaje_encriptado = cipher_suite.encrypt(mensaje_bytes)
    return mensaje_encriptado

def desencriptar_mensaje(mensaje_encriptado):
    mensaje_desencriptado = cipher_suite.decrypt(mensaje_encriptado)
    return mensaje_desencriptado.decode(FORMAT)

app = Flask(__name__)

# Función que registra el dron en la db
def registrarDron(alias, id, conn, coleccion):
    try:
        # Genero el token
        texto = str(randint(1, 10000000))
        sha256 = hashlib.sha256(texto.encode(FORMAT)).hexdigest()
        hora = datetime.now() + timedelta(seconds=20)
        # Recorto el hash para que así sea más difícil averiguar cómo se genera el token
        token = sha256[10:25]
        
        # Dron
        nuevo_dron = {"id": id, "alias": alias, "token": token, "hora": hora}
        
        # Inserto el nuevo dron en db
        coleccion.insert_one(nuevo_dron)
        
        print("Enviando mensaje al dron")
        conn.send(encriptar_mensaje(token))
        conn.close()
    except Exception as e:
        print("Error al registrar el dron")
        print(e)

def editarDron(id, alias, conn, coleccion):
    nuevo_valor = {
        "$set": {
            "alias": alias
        }
    }
    
    coleccion.update_one({"id": id}, nuevo_valor)
    conn.close()

def atenderPeticion(conn, addr):
    try:
        mensaje_recibido = conn.recv(HEADER)
        info = desencriptar_mensaje(mensaje_recibido).split(':')
        
        client = MongoClient(f"mongodb://{IP_BBDD}:{PORT_BBDD}")
        db = client['drones_db']
        coleccion = db['drones']
        
        print(f"He recibido {info[0]} de {addr}")
        
        if info[0] == "1":
            registrarDron(info[1], info[2], conn, coleccion)
        elif info[0] == "2":
            editarDron(info[1], info[3], conn, coleccion)
    except Exception as e:
        print("Se nos fue el cliente")

def iniciarSocketServer():
    PORT = os.getenv('PORT_REGISTRY')
    SERVER = os.getenv('IP_REGISTRY')
    
    socketReg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketReg.bind((SERVER, int(PORT)))
    socketReg.listen()

    print(f"Servidor Registro a la escucha en {PORT} {SERVER}")

    while True:
        print("Esperando conexión...")
        conn, addr = socketReg.accept()
        print(f"Nueva conexión: {addr}")

        thread = threading.Thread(target=atenderPeticion, args=(conn, addr))
        thread.start()

@app.route('/register', methods=['POST'])
def registrarApi():
    data = request.json
    drone_id = data.get('id')
    # Ciframos el id y lo usamos como token para mandar
    token = hashlib.sha256(drone_id.encode()).hexdigest()
    hora = datetime.now() + timedelta(seconds=20)
    # Dron
    nuevo_dron = {"id": drone_id, "alias": drone_id, "token": token, "hora": hora}
    # Inserto el nuevo dron en db
    client = MongoClient(f"mongodb://{IP_BBDD}:{PORT_BBDD}")
    db = client['drones_db']
    coleccion = db['drones']
    coleccion.insert_one(nuevo_dron)

    return jsonify({"message": "Dron registrado con éxito", "encoded_id": token}), 200

def iniciar_flask_server():
    app.run(host='0.0.0.0', port=PORT_API_REGISTRY)

def main():
    thread_socket = threading.Thread(target=iniciarSocketServer)
    thread_socket.start()

    threading.Thread(target=iniciar_flask_server).start()

if __name__ == '__main__':
    main()
