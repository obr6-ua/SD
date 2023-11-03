# from pymongo import MongoClient


import socket 
import threading
import sys
import os


FORMAT = 'utf-8'
HEADER = 4096

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

def registrarDron(alias, id , conn):
    # dbhilo = NucleoDB()
    
        # if(existeId(id, dbhilo)):
            # conn.send(f"(-1, 'Este id ya está registrado, prueba con otro')")
        # else:
    print("Enviando mensaje al dron")
    conn.send("123123".encode(FORMAT))
    conn.close()

# def editarJugador(alias, conn):
#     dbhilo = NucleoDB()
#     try:
#         if(existeAliasBD(alias, dbhilo) == False):
#             conn.send(f"(-1 ,'No se ha encontrado este alias')")
#         else:
#             if(dbhilo.loginCredenciales(alias,contraseña)):
#                 conn.send(f"(1 ,'Credenciales correctas')")
#                 infoNueva       = eval(conn.recv(HEADER))
#                 aliasNuevo      = infoNueva[0]
#                 contraseñaNueva = infoNueva[1]

#                 try:
#                     dbhilo.modificarCredenciales(alias, aliasNuevo, contraseñaNueva)
#                 except Exception as e:
#                     print(e)
#                     conn.send(f"(-1 ,'Fallo al actualizar usuario, por favor inténtalo más tarde')")
                    
#                 conn.send(f"(1 ,'Credenciales modificadas correctamente')")
#             else:
#                 conn.send(f"(-1 ,'Contraseña incorrecta')")
#     except Exception as e:
#         print("Se nos fue el cliente")
#         print(e)
    
#     conn.close()

def atenderPeticion(conn, addr):
    try:
        info = conn.recv(HEADER).decode(FORMAT)  # Decodificar el mensaje recibido

        print(f"He recibido {info} de {addr}")
        
        if info == "1":
            registrarDron(os.getenv("ALIAS"), os.getenv("ID"), conn)
        elif info == "2":
            editarDron(info[1], info[2], conn)
    except Exception as e:
        print("Se nos fue el cliente")

def iniciar():
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



def main():
    iniciar()
    
main()

