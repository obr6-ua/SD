
from Utils import *

import socket 
import threading
import sys
import os

FORMAT = 'utf-8'
HEADER = 128

if(os.getenv('entorno') == None):
    SERVER_CLIMA  = '0.0.0.0'
    SERVER_NUCLEO = '0.0.0.0'
else:
    SERVER_CLIMA  = '10.0.0.2'
    SERVER_NUCLEO = '10.0.0.3'

def resetCredenciales():
    confirmacion = input("¿Estás seguro? Esto borrará las credenciales de todos los jugadores s/n: ")
    if(confirmacion == "s"):
        db.borrar("credenciales")
        db.crear("credenciales")
    else:
        sys.exit(0)

def existeAliasBD(alias, dbhilo):
    if (dbhilo.buscarAliasCredenciales(alias)): return True 
    else: return False

def registrarJugador(alias, contraseña, conn):
    dbhilo = NucleoDB()
    try:
        if(existeAliasBD(alias, dbhilo)):
            conn.send(f"(-1, 'Este alias ya está registrado, prueba con otro')".encode(FORMAT))
        else:
            dbhilo.insertarCredenciales(alias,contraseña)
            conn.send(f"(1, 'Credenciales registradas correctamente')".encode(FORMAT))
    except Exception as e:
        print("Se nos fue el cliente")
        print(e)
    conn.close()

def editarJugador(alias, contraseña, conn):
    dbhilo = NucleoDB()
    try:
        if(existeAliasBD(alias, dbhilo) == False):
            conn.send(f"(-1 ,'No se ha encontrado este alias')".encode(FORMAT))
        else:
            if(dbhilo.loginCredenciales(alias,contraseña)):
                conn.send(f"(1 ,'Credenciales correctas')".encode(FORMAT))
                infoNueva       = eval(conn.recv(HEADER).decode(FORMAT))
                aliasNuevo      = infoNueva[0]
                contraseñaNueva = infoNueva[1]

                try:
                    dbhilo.modificarCredenciales(alias, aliasNuevo, contraseñaNueva)
                except Exception as e:
                    print(e)
                    conn.send(f"(-1 ,'Fallo al actualizar usuario, por favor inténtalo más tarde')".encode(FORMAT))
                    
                conn.send(f"(1 ,'Credenciales modificadas correctamente')".encode(FORMAT))
            else:
                conn.send(f"(-1 ,'Contraseña incorrecta')".encode(FORMAT))
    except Exception as e:
        print("Se nos fue el cliente")
        print(e)
    
    conn.close()

def atenderPeticion(conn, addr):

    try:
        msg = conn.recv(HEADER).decode(FORMAT)
        print(f"He recibido {msg} de {addr}")
        
        info = eval(msg)

        if(info[0] == 1):
            registrarJugador(info[1], info[2], conn)
        elif(info[0] == 2):
            editarJugador(info[1], info[2], conn)
    except Exception as e:
        print("Se nos fue el cliente")

def iniciar():
    args = sys.argv
    args.pop(0)
    if(comprobarArgs(args, "registry") == False): sys.exit(-1)
    print(args[0])

    PORT = int(args[0])
    SERVER = SERVER_NUCLEO

    socketReg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketReg.bind((SERVER,PORT))
    socketReg.listen()

    print(f"Servidor Registro a la escucha en {PORT} {SERVER}")

    while(True):
        print("Esperando conexión...")
        conn, addr = socketReg.accept()
        print(f"Nueva conexión: {addr}")

        thread = threading.Thread(target=atenderPeticion, args=(conn, addr))
        thread.start()



def main():
    print("Opciones:")
    print("1: Iniciar registry")
    print("2: Reset credenciales jugadores")

    op = int(input())

    if(op == 1):
        iniciar()
    elif(op == 2):
        resetCredenciales()

main()

