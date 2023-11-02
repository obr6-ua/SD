import os
import socket
import json

from random import randint

HOST = 'localhost'

def cargarCiudades(path):
    with open(path) as file:
        print("Cargando ciudades...")
        auxJson = json.load(file)
        return auxJson['lista']

def main():
    print("Iniciando AD_Weather...")
    puerto = os.getenv('PUERTO')

    socketClima = socket.socket()
    socketClima.bind((HOST, puerto))
    socketClima.listen(1)

    ciudades = cargarCiudades("ciudaddes.json")

    while True:
        conexion, addr = socketClima.accept()
        print("AD_Engine conectado.")

        ciudad = ciudades[randint(0, len(ciudades)-1)]

        conexion.send(str(ciudad).encode('utf-8'))

main()