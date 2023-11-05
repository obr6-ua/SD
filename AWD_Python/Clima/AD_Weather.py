import os
import socket
import json

from random import randint

HOST = '0.0.0.0'

def cargarCiudades(path):
    with open(path) as file:
        print("Cargando ciudades...")
        auxJson = json.load(file)
        return auxJson['lista']

def main():
    print("Iniciando AD_Weather...")
    puerto = os.getenv('PUERTO')

    socketClima = socket.socket()
    socketClima.bind((HOST, int(puerto)))
    socketClima.listen(1)

    ciudades = cargarCiudades("ciudades.json")

    while True:
        conexion, addr = socketClima.accept()
        print("AD_Engine conectado.")

        ciudad = ciudades[randint(0, len(ciudades) - 1)]
        ciudad_json = json.dumps(ciudad)  # Convierte la ciudad en una cadena JSON válida

        conexion.send(ciudad_json.encode('utf-8'))
main()