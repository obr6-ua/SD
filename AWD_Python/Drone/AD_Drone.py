from kafka import KafkaConsumer, KafkaProducer
from multiprocessing import Process
from json import loads
import json

import sys
import socket
import os


# from colorama import Fore, Back, Style

#docker-compose run -e ID=1 -p 4001:4000 drone

FORMAT = 'utf-8'
HEADER = 4096
KTAMANYO = 20

class AD_Drone:
    def __init__(self, id=os.getenv("ID"), alias=None, token=None, x=1, y=1, finalx=None, finaly=None , topicConsumidor='engine_drones', topicProductor= 'drones_engine' , consumer=None , producer=None, state=False):
        self.id = id
        self.alias = alias
        self.token = token
        self.x = x
        self.y = y
        self.finalx = finalx
        self.finaly = finaly
        self.topicConsumidor = topicConsumidor
        self.topicProductor =  topicProductor
        self.consumer = consumer
        self.producer = producer
        self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]
        self.state = state


    def editUser(self, host, port):
        ADDR_REGISTRO = (host, port)
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR_REGISTRO)
            print (f"Establecida conexión en [{ADDR_REGISTRO}]")

            alias = input("Alias antiguo: ")
            alias2 = input("Nuevo alias: ")

            cadena = "1:" + self.id + ":" + alias + ':' + alias2

            client.send(cadena.encode(FORMAT))

            self.alias = client.recv(HEADER).decode(FORMAT)

            print('Nuevo alias asignado.')
        except Exception as e:
            print("Fallo con el servidor de Registry")
            print(e)

        client.close()

    def registro(self, host, port):
        try:
            ADDR_REGISTRO = (host, port)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR_REGISTRO)
            self.alias = input("Alias nuevo: ")
            print(f"Establecida conexión en [{ADDR_REGISTRO}]")

            cadena = "1:" + self.id + ":" + self.alias

            client.send(cadena.encode(FORMAT))

            self.token = client.recv(HEADER).decode(FORMAT)

            print(f"He recibido el mensaje del Registry: {self.token}")
            
            
            return self

        except Exception as e:
            print("Error al conectar con el servidor de Registro")
            print(e)

        client.close()

    def iniciarKafka(self):
        kafka = os.getenv('IP')+':'+ os.getenv('PORT_KAFKA')
        # Creamos consumidor
        self.consumer = KafkaConsumer(
            self.topicConsumidor,
            bootstrap_servers=[kafka],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='drones',
            value_deserializer=lambda x: loads(x.decode('utf-8')))

        # Creamos productor
        self.producer = KafkaProducer(bootstrap_servers=[kafka],
                                    value_serializer=lambda x: 
                                    json.dumps(x).encode('utf-8'))

    def printMap(self):
        print("   ", end="")
        for j in range(1, KTAMANYO + 1):
            print(f"{j:4}", end=" ")
        print()

        # Imprimir la matriz con los números de fila en el borde izquierdo
        for i in range(1, KTAMANYO):
            # Imprimir el número de fila en el borde izquierdo
            print(f"{i:3} ", end="")

            # Imprimir espacio en blanco en lugar de los valores de la matriz
            for j in range(1, KTAMANYO):
                elemento = self.mapa[i][j]
                print(f"{elemento:4}", end=" ")
            print()


    def logearse(self, host, port):
        ADDR_log = (host, port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(ADDR_log)
            print(self.token)
        except:
            print("El servidor está desconectado.")
            client.close()
            return

        print(f"Establecida conexión en [{ADDR_log}]")

        client.send(str(self.token).encode(FORMAT))

        recibido = client.recv(HEADER).decode(FORMAT)

        recibido = recibido.split(':')  # Corregir esta línea

        self.finalx = recibido[0]
        self.finaly = recibido[1]

        self.iniciarKafka()
        
        
        while not self.state:
            print('Esperando mensaje del engine') 
            for message in self.consumer:
                print('Lo tengo')
                #data = json.loads(message.value.decode('utf-8'))
                self.mapa = message.value #data
                self.producer.send(self.topicProductor, value=self.Movimiento())
                self.printMap()
            
    
    #Funcion que indica el movimimiento del dron. Si no se mueve indica que ha completado y actualiza el estado del dron
    def Movimiento(self):
        if self.finalx > self.x:
            return self.id+':'+'E'
        elif self.finalx < self.x:
            return self.id+':'+'W'
        else :
            if self.finaly > self.y:
                return self.id+':'+'N'
            elif self.finaly < self.y:
                return self.id+':'+'S'
            else:
                self.state = True
                return self.id+':'+'COMPLETADO'


            
    # ip y puerto engine, ip y puerto del kafka, ip y puerto de registry
    def main(self):
        opcion = ""
        while opcion != "5":
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
            opcion = res
            if res == "1":
                self.editUser(os.getenv("IP"), int(os.getenv("PORT")))
            elif res == "2":
                self.registro(os.getenv("IP"), int(os.getenv("PORT")))
            elif res == "3":
                self.logearse(os.getenv("IP"), int(os.getenv("PORT_ENGINE")))
            elif res == "4":
                pass
                # alias = input("¿Cuál era tu alias?: ")
                # iniciarKafka(alias)

if __name__ == "__main__":
    drone = AD_Drone()
    drone.main()