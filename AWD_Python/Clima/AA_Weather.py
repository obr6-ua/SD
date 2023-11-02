import json
import sys
import socket
import os

from Utils import *
from random import randint

HEADER = 128
FORMAT = 'utf-8'

if(os.getenv('entorno') == None):
    SERVER_CLIMA  = '0.0.0.0'
else:
    SERVER_CLIMA  = '10.0.0.2'

def cargarCiudades(path):
    with open(path) as file:
        print("Cargando ciudades...")
        auxJson = json.load(file)
        return auxJson['lista']


def main():
    print("Iniciando servicio clima...")

    args = sys.argv
    args.pop(0)

    if(comprobarArgs(args) == False): sys.exit(-1)

    HOST = SERVER_CLIMA # CAMBIAR HOST PARA DOCKER
    PORT = int(args[0])

    socketClima = socket.socket()
    socketClima.bind((HOST, PORT))
    socketClima.listen(4)

    print (f"Servidor clima creado y a la escucha en {HOST} {PORT}")

    ciudades = cargarCiudades("ciudades.json")

    while(True):
        print("Esperando conexión...")
        conexion, addr = socketClima.accept()
        print (f"Nueva conexion: {addr}")

        print("Generando ciudad aleatoria...")
        ciudad = ciudades[randint(0, len(ciudades)-1)]

        conexion.send(str(ciudad).encode(FORMAT))
        print(f"Ciudad enviada: {str(ciudad)}")

main()
