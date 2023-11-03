# from kafka import KafkaConsumer, KafkaProducer
from multiprocessing import Process

import sys
import socket
import os

# from colorama import Fore, Back, Style

FORMAT = 'utf-8'
HEADER = 4096
POSSIBLE_MOVES = ['w', 'a', 's', 'd', 'aw', 'wa', 'wd', 'dw', 'sd', 'ds', 'as', 'sa']

def editUser(host, port):
    ADDR_REGISTRO = (host, port)
    token = "a"
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR_REGISTRO)
        print (f"Establecida conexión en [{ADDR_REGISTRO}]")

        usuario = input("Alias antiguo: ")
        user_info = (2, usuario)

        client.send(str(user_info))

        recibido = client.recv(100)
        respuesta = eval(recibido)

        if(respuesta[0] == -1):
            print(respuesta[1])
            return

        else:
            print(respuesta[1])
            alias_new  = input("Alias nuevo: ")

            msg = (alias_new)
            client.send(str(msg))

            respuesta = eval(client.recv(100))
            print(respuesta[0])
            token = respuesta[0]
    except Exception as e:
        print("Fallo con el servidor de Registry")
        print(e)

    client.close()

def registro(host, port):
    try:
        ADDR_REGISTRO = (host, port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR_REGISTRO)

        print(f"Establecida conexión en [{ADDR_REGISTRO}]")


        client.send("1".encode(FORMAT))  # Enviar la solicitud codificada en bytes

        respuesta = eval(client.recv(HEADER).decode(FORMAT))  # Recibir y decodificar la respuesta

        if respuesta[0] == -1:
            print(respuesta[1])
        else:
            print(respuesta[1])

            # Recibir el mensaje del Registry
            mensaje_del_registry = client.recv(100).decode(FORMAT)
            print(f"He recibido el mensaje del Registry: {mensaje_del_registry}")

    except Exception as e:
        print("Error al conectar con el servidor de Registro")
        print(e)

    client.close()



def logearse(host, port):
    ADDR_log = (host, port) 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR_log)
    except:
        print("El servidor está desconectado o ya hay una partida en curso")
        client.close()
        return

    print (f"Establecida conexión en [{ADDR_log}]")

    ## Confirmación conexión
    recibido = client.recv(HEADER)
    msg = eval(recibido)


    if(msg[0] == 1):
        alias = input("Introduce alias: ")

        clientmsg = (alias)

        try:
            ## Enviar alias
            client.send(str(clientmsg))

            ## code 1: login correcto
            recibido = client.recv(HEADER)

            msg = eval(recibido)
            if(msg[0] == -1):
                print(msg[1])
                return

            elif(msg[0] == 1):
                print(msg[1])
                print("Esperando a que el servidor inicie el juego")

                while(True):
                    try:
                        esperaPartida = client.recv(HEADER).decode(FORMAT)
                    except:
                        print("Fallo con el servidor mientras se esperaba la partida")
                        client.close()
                        return
                        
                    msg = eval(esperaPartida)

                    if(msg[0] == 2):
                        print("Empieza la partida")
                        print(msg[1])
                        iniciarKafka(alias)
                    else:
                        print(msg[1])

        except Exception as e:
            print("Parece que hemos tenido un problema con el servidor, prueba más tarde")
            print(e)
            client.close()
            return

    elif(msg[0] == -1):
        print("Ya no caben mas jugadores")
        client.close()
        return

    client.close()

# def pedirMovimiento(dron):
#     while(mov not in POSSIBLE_MOVES):
        
#         dron

#     return mov

# def consumirMapa():
#     try:
#         mapConsumer = KafkaConsumer('map',bootstrap_servers=SERVER_KAFKA)
        
#         for mapa in mapConsumer:
#             msg = mapa.value.decode(FORMAT)

#             if('FIN DE PARTIDA' in msg):
#                 print('\n')
#                 print(msg)
#                 return
#             else:
#                 print(msg)
#     except:
#         print("Hemos tenido un problema con el servidor de Streaming (mapa)")
#         return



# def producirMov(alias, fn):
#     try:
#         movProducer = KafkaProducer(bootstrap_servers=SERVER_KAFKA)
#         sys.stdin = os.fdopen(fn)  #open stdin in this process

#         while(True):
#             mov = pedirMovimiento()
#             movProducer.send('moves', f"('{alias}', '{mov}')".encode(FORMAT))
#             movProducer.flush()
#     except:
#         print("Hemos tenido un problema con el servidor de Streaming (movimientos)")
#         return

# def iniciarKafka(alias):

#     fn = sys.stdin.fileno()
#     procesoConsumer = Process(target=consumirMapa)
#     procesoProducer = Process(target=producirMov, args=(alias,fn))

#     procesoConsumer.start()
#     procesoProducer.start()

#     while(procesoConsumer.is_alive()):
#         if(procesoProducer.is_alive() == False):
#             break

#     procesoConsumer.terminate()
#     procesoProducer.terminate()

#     print("Gracias por jugar a nuestro juego!")
#     sys.exit(0)
        
# ip y puerto engine, ip y puerto del kafka, ip y puerto de registry
def main(): 
    global SERVER_KAFKA
    opcion = ""
    while(opcion != "5"):
        print("///////////////////////////////////////")
        print("// BIENVENIDO AL ESPECTACULO         //")
        print("//                                   //")
        print("// Menu:                             //")
        print("// 1. Editar dron                    //")
        print("// 2. Crear dron                     //")
        print("// 3. Entrar a la partida            //")
        print("// 4. Retomar partida (desconexión)  //")
        print("// 5. Salir                          //")
        print("///////////////////////////////////////")
        res = input("Introduce la opcion que quieras hacer: ")
        # SERVER_KAFKA = sys.argv[2].split(":")[0] # Seria el 3
        ## python3 player 10.0.0.2:3000 (kafka) 10.0.0.2:3002
        opcion = res
        if res == "1":
            #Opcion 1 se conecta por sockets al registry
            editUser(os.getenv("IP"), int(os.getenv("PORT")))
        elif res == "2": 
            registro(os.getenv("IP"), int(os.getenv("PORT")))
            #Opcion 2 se conecta por sockets al registry
        elif res == "3":
            #Por sockets se conectan al engine pasandole alias + password
            logearse(os.getenv("IP_ENGINE") , int(os.getenv("PORT_ENGINE")), )
        elif res == "4":
            ""
            # alias = input("¿Cuál era tu alias?: ")
            # iniciarKafka(alias)



if __name__ == "__main__":
    main()
