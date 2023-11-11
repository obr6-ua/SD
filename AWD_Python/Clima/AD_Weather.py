import os
import socket
import json

from random import randint

HOST = '0.0.0.0'

def main():
    print("Iniciando AD_Weather...")
    puerto = os.getenv('PUERTO')

    socketClima = socket.socket()
    socketClima.bind((HOST, int(puerto)))
    socketClima.listen(1)

    while True:
        conexion, addr = socketClima.accept()
        print("AD_Engine conectado.")

        temperatura = randint(1, 15)

        conexion.send(str(temperatura).encode('utf-8'))
main()