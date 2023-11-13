import os
import socket
import json
import random
import time

def main():

    with open('ciudades.json', 'r') as file:
        ciudades = json.load(file)
    
    ciudad_elegida = random.choice(ciudades["Ciudades"])
    
    socketClima = socket.socket()
    socketClima.bind(('0.0.0.0', int(os.getenv('PUERTO'))))
    socketClima.listen(1)

    while True:
        conexion, addr = socketClima.accept()
        print("AD_Engine conectado.")
        
        # Seleccionar la tercera ciudad y una temperatura aleatoria de esa ciudad
        ciudad_elegida = ciudades["Ciudades"][2]  # Tercera ciudad (Valencia)
        temperatura_aleatoria = random.choice(ciudad_elegida["Temperatura"])

        conexion.send(str(temperatura_aleatoria).encode('utf-8'))
        conexion.close()
main()