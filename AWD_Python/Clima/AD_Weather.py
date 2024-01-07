import os
import socket
import json
import random
import time
import requests


def main():

    with open('ciudades.json', 'r') as file:
        ciudades = json.load(file)
    
    ciudad_elegida = random.choice(ciudades["Ciudades"])
    
    socketClima = socket.socket()
    socketClima.bind(('0.0.0.0', int(os.getenv('PUERTO'))))
    socketClima.listen(1)

    CLAVE_API = 'e45bbc8bfead4e3311fdac9a7e9dd78c'
    
    while True:
        conexion, addr = socketClima.accept()
        print("AD_Engine conectado.")
        
        # Seleccionar la tercera ciudad y una temperatura aleatoria de esa ciudad
        ciudad_elegida = random.choice(ciudades["Ciudades"])  # Tercera ciudad (Valencia)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad_elegida}&appid={CLAVE_API}"
        
        respuesta = requests.get(url)
        datos = respuesta.json()
        print(datos)

        conexion.send(str(respuesta).encode('utf-8'))
        conexion.close()
main()