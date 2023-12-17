from pymongo import MongoClient
from random import randint
#Practica 3
from flask import Flask, request, jsonify
from datetime import datetime, timedelta


import hashlib
import socket 
import threading
import sys
import os
#Practica 3
import threading

FORMAT = 'utf-8'
HEADER = 4096

app = Flask(__name__)

# Inicializamos la base de datos
# cliente = MongoClient(os.getenv('IP_BBDD') +':'+ os.getenv('PORT_BBDD'))

# bd = cliente['AWD']
# coleccion1 = bd['ID-ALIAS']

# def resetCredenciales():
#     confirmacion = input("¿Estás seguro? Esto borrará las credenciales de todos los jugadores s/n: ")
#     if(confirmacion == "s"):
#         db.borrar("credenciales")
#         db.crear("credenciales")
#     else:
#         sys.exit(0)

# def existeAliasBD(alias, dbhilo):
#     if (self.coleccion1.find_one({"ID": id, "token": token})): return True 
#     else: return False

#Funcion que me registra el dron en la db
def registrarDron(alias, id , conn , coleccion):
    try: 
        #Genero el token
        texto = str(randint(1 , 10000000))
        sha256 = hashlib.sha256(texto.encode()).hexdigest()
        
        #Recorto el hash para que asi sea mas dificil averiguar como se genera el token
        token = sha256[10:25]
        
        #Dron
        nuevo_dron = {"id": id, "alias" : alias, "token" : token}
        
        #Inserto el nuevo dron en db
        coleccion.insert_one(nuevo_dron)
        
        print("Enviando mensaje al dron")
        conn.send(token.encode(FORMAT))
        conn.close()
    except Exception as e:
        print("ME CAGO EN DIOS")
        print(e)
    
    

def editarDron(id, alias, conn , coleccion):
    
    nuevo_valor = {
        "$set": {
            "alias": alias # Agrega los campos y valores que deseas actualizar
        }
    }
    
    coleccion.update_one({"id": id}, nuevo_valor)
    
    conn.close()

def atenderPeticion(conn, addr):
    try:
        info = conn.recv(HEADER).decode(FORMAT)  # Decodificar el mensaje recibido
        info.split(':')
        
        client = MongoClient("mongodb://192.168.23.1:27017")
    
        db = client['drones_db']
        
        coleccion = db['drones']
        
        print(f"He recibido {info[0]} de {addr}")
        
        if info[0] == "1":
            registrarDron(info[1], info[2], conn , coleccion)
        elif info[0] == "2":
            editarDron(info[1], info[3], conn , coleccion)
    except Exception as e:
        print("Se nos fue el cliente")

def iniciarSocketServer():
    PORT = os.getenv('PORT_REGISTRY')
    SERVER = os.getenv('IP_REGISTRY')
    

    socketReg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketReg.bind((SERVER,int(PORT)))
    socketReg.listen()

    print(f"Servidor Registro a la escucha en {PORT} {SERVER}")

    while(True):
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
    #Dron
    nuevo_dron = {"id": drone_id, "alias" : drone_id, "token" : token, "hora" : hora}
    #Inserto el nuevo dron en db
    client = MongoClient("mongodb://192.168.23.1:27017")
    db = client['drones_db']
    coleccion = db['drones']
    coleccion.insert_one(nuevo_dron)

    return jsonify({"message": "Dron registrado con éxito", "encoded_id": token}), 200

def iniciar_flask_server():
    app.run(debug=True, host='0.0.0.0', port=5000)

def main():
    thread_socket = threading.Thread(target=iniciarSocketServer)
    thread_socket.start()

    # Iniciar el servidor Flask en otro hilo
    threading.Thread(target=iniciar_flask_server).start()

    
main()

