from dataclasses import dataclass
from random import randint, choice
from NucleoDB import NucleoDB

import socket
import string

HEADER = 128
FORMAT = 'utf-8'

def comprobarArgs(args, modulo):
        if(modulo == "engine"):
            if(len(args) != 3):
                print("Deben haber 3 argumentos exactos")
                return False

        elif(modulo == "registry"):
            if(len(args) != 1):
                print("Debe haber 1 argumento exacto")
                return False


        for arg in args:
            try:
                int(arg)
            except:
                print("Los argumentos deben ser números enteros")
                return False

        print("Argumentos OK")
        return True

def obtenerCiudades(host,port):
    listaCiudades = []
    print(f"Obteniendo ciudades de {host} {port}")

    for _ in range(4):
        socketClima = socket.socket()
        socketClima.connect((host,port))
        ciudad = socketClima.recv(HEADER).decode(FORMAT)
        listaCiudades.append(eval(ciudad))
        socketClima.close()

    return listaCiudades

def mover(posicion, mov : str):
    x = posicion[0]
    y = posicion[1]

    mov = mov.lower()

    if(mov == 'aw' or mov == 'wa'):
        x -= 1
        y -= 1
    elif(mov == 'w'):
        x -= 1
    elif(mov == 'wd' or mov == 'dw'):
        x -= 1
        y += 1
    elif(mov == 'd'):
        y+= 1
    elif(mov == 'sd' or mov == 'ds'):
        x += 1
        y += 1
    elif(mov == 's'):
        x += 1
    elif(mov == 'as' or mov == 'sa'):
        x += 1
        y -= 1
    elif(mov == 'a'):
        y -= 1

    if(x < 0 or x > 19 or y < 0 or y > 19):
        raise Exception("Fuera del límite del mapa")
    else:
        return (x,y)


@dataclass
class Dron:
    alias : string
    pos : tuple
    estado : bool

def crearDron(alias) -> Dron:
    pos = (1 , 1)
    estado = False
    return Dron(alias, pos, estado)