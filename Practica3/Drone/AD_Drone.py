from kafka import KafkaConsumer, KafkaProducer
from multiprocessing import Process
from json import loads
import json
import time
import sys
import socket
import os
#Practica 3
import requests

from prettytable import PrettyTable
from cryptography.fernet import Fernet
from datetime import datetime

#docker-compose run -e ID=1 -p 4001:4000 drone

FORMAT = 'utf-8'
HEADER = 4096
KTAMANYO = 20
URL_REGISTRY = "http://0.0.0.0:5000"
URL_ENGINE = "http://0.0.0.0:5000"
clave_encriptada = os.getenv('CLAVE_ENCRIPTADA').encode()
cipher_suite = Fernet(clave_encriptada)

# Función para encriptar un mensaje
def encriptar_mensaje(mensaje):
    mensaje_bytes = mensaje.encode()
    mensaje_encriptado = cipher_suite.encrypt(mensaje_bytes)  # Encriptar
    return mensaje_encriptado

# Función para desencriptar un mensaje
def desencriptar_mensaje(mensaje_encriptado):
    mensaje_desencriptado = cipher_suite.decrypt(mensaje_encriptado)  # Desencriptar
    return mensaje_desencriptado.decode() 

class AD_Drone:
    def __init__(self, id=os.getenv("ID"), api=os.getenv("API"), alias=None, token=None, x=1, y=1, finalx=None, finaly=None, state=False):
        self.id = id
        self.api = api
        self.alias = alias
        self.token = token
        self.x = x
        self.y = y
        self.finalx = finalx
        self.finaly = finaly
        self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]
        self.state = state

    def registro(self, host, port):
        try:
            ADDR_REGISTRO = (host, port)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR_REGISTRO)
            #print(f"Establecida conexión en [{ADDR_REGISTRO}]")
            #escribir_log(f"Dron {self.id} conectado a Registry. {datetime.now()}")

            cadena = "1:" + self.id + ":" + self.id

            client.send(encriptar_mensaje(cadena.encode(FORMAT)))

            self.token = desencriptar_mensaje(client.recv(HEADER).decode(FORMAT))

            #print(f"He recibido el mensaje del Registry: {self.token}")
            #escribir_log(f"Dron {id} ha recibido token del Registry. {datetime.now()}")
            
            return self

        except Exception as e:
            print("Error al conectar con el servidor de Registro")
            print(e)

        client.close()

    def registroApi(self, url_registry):
        respuesta = requests.post(url_registry + '/register', json={'id': self.id})
        if respuesta.status_code == 200:
            self.token = respuesta.json().get('encoded_id')
            #print(f"He recibido el mensaje del Registry: {self.token}")
            #escribir_log(f"Dron {self.id} ha recibido el mensaje del Registry: {self.token}. {datetime.now()}")
        else:
            return respuesta.status_code
            #print("Error en la solicitud:", respuesta.status_code)
            #escribir_log(f"Dron {self.id}: error contactando a Registry {datetime.now()}")


    def printMap(self):
        table = PrettyTable()
        header = [""] + [str(j) for j in range(1, KTAMANYO)]
        table.field_names = header

        for i in range(1, KTAMANYO):
            row = [str(i)] + [self.mapa[j][i] for j in range(1, KTAMANYO)]
            table.add_row(row)

        print(table)



    def logearse(self, host, port , producer , consumer):
        # Log en Engine por socket
        #if self.api == 'N':
        ADDR_log = (host, port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(ADDR_log)
            #print(self.token)
        except:
            #print("El servidor está desconectado.")
            #escribir_log(f"Dron {self.id}: El servidor está desconectado. {datetime.now()}")
            client.close()
            return

            #print(f"Establecida conexión en [{ADDR_log}]")
            #escribir_log(f"Dron {self.id}: Establecida conexión en [{ADDR_log}]. {datetime.now()}")
            client.send(encriptar_mensaje(str(self.token).encode(FORMAT)))
            recibido = desencriptar_mensaje(client.recv(HEADER).decode(FORMAT))
        #Log en Engine por API
        else:
            respuesta = requests.post(URL_ENGINE + '/register', json={'token': self.token})
            if respuesta.status_code == 200:
                recibido = respuesta.json().get('coordenadas')
            else:
                #print("Error en la solicitud:", respuesta.status_code)
                #print("Token expirado")
                #escribir_log(f"Dron {self.id}: Error en la solicitud: {respuesta.status_code}. {datetime.now()}")
                return 
        
        #print("Mensaje recibido del Engine", flush=True)
        #escribir_log(f"Dron {self.id}: Mensaje recibido del Engine. {datetime.now()}")
        if recibido != '':
            #print(recibido)
            recibido = recibido.split(':')

            self.finalx = int(recibido[0])
            self.finaly = int(recibido[1])

            #self.iniciarKafka()
            fin = False
            while not fin:
                if not self.state:
                    producer.send('drones_engine', value=encriptar_mensaje(self.Movimiento().encode('utf-8')))
                
                msg_poll = consumer.poll(timeout_ms=1000)

                for _, messages in msg_poll.items():
                    for message in messages:
                        if desencriptar_mensaje(message.value) == 'RESET':
                            #print('Estoy reseteando...')
                            #escribir_log(f"Dron {self.id}: Preparando nueva figura... {datetime.now()}")
                            self.x = 1
                            self.y = 1
                            self.state = False
                            fin = self.logearse(host, port , producer, consumer)
                            return True
                        
                        elif desencriptar_mensaje(message.value) == 'CANCELADO':
                            #print("CONDICIONES CLIMATICAS ADVERSAS. ESPECTACULO FINALIZADO")
                            return False
                        
                        elif desencriptar_mensaje(message.value) == 'FIN':
                            client.close()
                            return True
                        else:
                            self.mapa = desencriptar_mensaje(message.value)
                            self.printMap()
                            time.sleep(0.1)

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
        if self.api == 'N':
            self.registro(os.getenv("IP"), int(os.getenv("PORT")))
        else:
            self.registroApi(URL_REGISTRY)

        kafka = os.getenv('IP')+':'+ os.getenv('PORT_KAFKA')
        # Creamos consumidor
        consumer = KafkaConsumer(
            'engine_drones',
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