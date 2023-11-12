from kafka import KafkaConsumer, KafkaProducer
from multiprocessing import Process
from json import loads
import json
import time
import sys
import socket
import os
from prettytable import PrettyTable


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
            print(f"Establecida conexión en [{ADDR_REGISTRO}]")

            cadena = "1:" + self.id + ":" + self.id

            client.send(cadena.encode(FORMAT))

            self.token = client.recv(HEADER).decode(FORMAT)

            print(f"He recibido el mensaje del Registry: {self.token}")
            
            return self

        except Exception as e:
            print("Error al conectar con el servidor de Registro")
            print(e)

        client.close()

    def printMap(self):
        table = PrettyTable()
        header = [""] + [str(j) for j in range(1, KTAMANYO)]
        table.field_names = header

        for i in range(1, KTAMANYO):
            row = [str(i)] + [self.mapa[j][i] for j in range(1, KTAMANYO)]
            table.add_row(row)

        print(table)



    def logearse(self, host, port , producer , consumer):
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
        
        print("Mensaje recibido del Engine", flush=True)
        if recibido != '':
            print(recibido)
            recibido = recibido.split(':')  # Corregir esta línea

            self.finalx = int(recibido[0])
            self.finaly = int(recibido[1])

            #self.iniciarKafka()

            
            fin = False
            while fin is False:
                if not self.state:
                    time.sleep(1)
                    producer.send(self.topicProductor, value=self.Movimiento().encode('utf-8'))
                
                msg_poll = consumer.poll(timeout_ms=1000)
                if msg_poll is None:
                    continue  # No hay mensajes, sigue esperando

                for _, messages in msg_poll.items():
                    for message in messages:
                        print('Lo tengo')
                        if message.value == 'RESET':
                            print('Estoy reseteando...')
                            self.x = 1
                            self.y = 1
                            self.state = False
                            fin = self.logearse(host, port , producer, consumer)
                        else:
                            self.mapa = message.value # Accede directamente al valor de la tupla
                            self.printMap()
        client.close()
        print('FIGURAS COMPLETADAS HIJODEPUTA')
        print('DIBLOOOO QUE GANSTER!!!')
        
        return True
            
                
        
    
    #Funcion que indica el movimimiento del dron. Si no se mueve indica que ha completado y actualiza el estado del dron
    def Movimiento(self):
        if self.finalx > self.x:
            self.x += 1
            return str(self.id) + ":" + str(self.x) + ":" + str(self.y) +':'+'E'
        elif self.finalx < self.x:
            self.x -= 1
            return  str(self.id) + ":" + str(self.x) + ":" + str(self.y)+':'+'W'
        else :
            if self.finaly > self.y:
                self.y += 1
                return  str(self.id) + ":" + str(self.x) + ":" + str(self.y)+':'+'S'
            elif self.finaly < self.y:
                self.y -= 1
                return  str(self.id) + ":" + str(self.x) + ":" + str(self.y)+':'+'N'
            else:
                self.state = True
                return  str(self.id) + ":" + str(self.x) + ":" + str(self.y) +':'+'COMPLETADO'


            
    # ip y puerto engine, ip y puerto del kafka, ip y puerto de registry
    def main(self):
        
            self.registro(os.getenv("IP"), int(os.getenv("PORT")))

            kafka = os.getenv('IP')+':'+ os.getenv('PORT_KAFKA')
            # Creamos consumidor
            consumer = KafkaConsumer(
                self.topicConsumidor,
                bootstrap_servers=[kafka],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda x: loads(x.decode('utf-8')))

            # Creamos productor
            producer = KafkaProducer(bootstrap_servers=[kafka])      
            self.logearse(os.getenv("IP"), int(os.getenv("PORT_ENGINE")) , producer , consumer)


if __name__ == "__main__":
    drone = AD_Drone()
    drone.main()