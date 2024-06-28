from kafka import KafkaConsumer, KafkaProducer
from json import loads
import json
import time
import socket
import os
import requests
from prettytable import PrettyTable
from cryptography.fernet import Fernet
from datetime import datetime

FORMAT = 'utf-8'
HEADER = 4096
KTAMANYO = 20
URL_REGISTRY = F"http://{os.getenv('IP_REGISTRY')}:{os.getenv('PORT_REGISTRY_API')}"
URL_ENGINE = f"http://{os.getenv('IP_ENGINE')}:{os.getenv('PORT_ENGINE_API')}"
clave_encriptada = os.getenv('CLAVE_ENCRIPTADA').encode()
cipher_suite = Fernet(clave_encriptada)

# Función para encriptar un mensaje
def encriptar_mensaje(mensaje):
    if isinstance(mensaje, str):
        mensaje_bytes = mensaje.encode(FORMAT)
    else:
        mensaje_bytes = mensaje
    mensaje_encriptado = cipher_suite.encrypt(mensaje_bytes)
    return mensaje_encriptado

# Función para desencriptar un mensaje
def desencriptar_mensaje(mensaje_encriptado):
    mensaje_desencriptado = cipher_suite.decrypt(mensaje_encriptado)
    return mensaje_desencriptado.decode(FORMAT)

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
            print(f"Establecida conexión en [{ADDR_REGISTRO}]")
            cadena = f"1:{self.id}:{self.id}"
            mensaje_encriptado = encriptar_mensaje(cadena)
            client.send(mensaje_encriptado)
            mensaje_recibido = client.recv(HEADER)
            self.token = desencriptar_mensaje(mensaje_recibido)
            return self
        except Exception as e:
            print("Error al conectar con el servidor de Registro")
            print(e)
        finally:
            client.close()

    def registroApi(self, url_registry):
        respuesta = requests.post(url_registry + '/register', json={'id': self.id})
        if respuesta.status_code == 200:
            self.token = respuesta.json().get('encoded_id')
        else:
            print("Error en la solicitud:", respuesta.status_code)

    def printMap(self):
        table = PrettyTable()
        header = [""] + [str(j) for j in range(KTAMANYO)]
        table.field_names = header
        for i in range(KTAMANYO):
            row = [str(i)] + [self.mapa[i][j] for j in range(KTAMANYO)]
            table.add_row(row)
        print(table)

    def logearse(self, host, port, producer, consumer):
        if self.api == 'N':
            ADDR_log = (host, port)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect(ADDR_log)
                print(f"Token enviado: {self.token}")
            except Exception as e:
                print(f"Error al conectar con el servidor Engine en {ADDR_log}: {e}")
                client.close()
                return
            try:
                if isinstance(self.token, bytes):
                    mensaje_encriptado = encriptar_mensaje(self.token)
                else:
                    mensaje_encriptado = encriptar_mensaje(self.token.encode(FORMAT))
                client.send(mensaje_encriptado)
                recibido = client.recv(HEADER)
                print(f"Mensaje recibido encriptado: {recibido}")
                recibido_desencriptado = desencriptar_mensaje(recibido)
                print(f"Mensaje recibido desencriptado: {recibido_desencriptado}")
            except Exception as e:
                print(f"Error durante la comunicación con el servidor Engine en {ADDR_log}: {e}")
                client.close()
                return
        else:
            try:
                respuesta = requests.post(URL_ENGINE + '/register', json={'token': self.token})
                if respuesta.status_code == 200:
                    recibido = respuesta.json().get('coordenadas')
                    print(f"Respuesta recibida del Engine: {recibido}")
                    recibido_desencriptado = recibido
                else:
                    print(f"Error en la solicitud: {respuesta.status_code}, mensaje: {respuesta.text}")
                    return
            except requests.ConnectionError as e:
                print("Error de conexión al servidor Engine")
                print(e)
                return
            except Exception as e:
                print("Error durante el registro en el servidor Engine")
                print(e)
                return

        if recibido_desencriptado:
            recibido_desencriptado = recibido_desencriptado.split(':')
            self.finalx = int(recibido_desencriptado[0])
            self.finaly = int(recibido_desencriptado[1])
            fin = False
            while not fin:
                if not self.state:
                    producer.send('drones_engine', value=encriptar_mensaje(self.Movimiento().encode('utf-8')))
                msg_poll = consumer.poll(timeout_ms=1000)
                for _, messages in msg_poll.items():
                    for message in messages:
                        mensaje_desencriptado = desencriptar_mensaje(message.value)
                        if mensaje_desencriptado == 'RESET':
                            self.x = 1
                            self.y = 1
                            self.state = False
                            fin = self.logearse(host, port, producer, consumer)
                            return True
                        elif mensaje_desencriptado == 'CANCELADO':
                            print("CONDICIONES CLIMATICAS ADVERSAS. ESPECTACULO FINALIZADO")
                            return False
                        elif mensaje_desencriptado == 'FIN':
                            time.sleep(100)
                            client.close()
                            return True
                        else:
                            self.updateMap(mensaje_desencriptado)
                            self.printMap()
                            time.sleep(0.1)

    def updateMap(self, mapa_actualizado):
        mapa = json.loads(mapa_actualizado)
        for i in range(KTAMANYO):
            for j in range(KTAMANYO):
                self.mapa[i][j] = mapa[i][j]

    def Movimiento(self):
        if self.finalx > self.x:
            self.x += 1
            return str(self.id) + ":" + str(self.x) + ":" + str(self.y) + ':' + 'E'
        elif self.finalx < self.x:
            self.x -= 1
            return str(self.id) + ":" + str(self.x) + ":" + str(self.y) + ':' + 'W'
        else:
            if self.finaly > self.y:
                self.y += 1
                return str(self.id) + ":" + str(self.x) + ":" + str(self.y) + ':' + 'S'
            elif self.finaly < self.y:
                self.y -= 1
                return str(self.id) + ":" + str(self.x) + ":" + str(self.y) + ':' + 'N'
            else:
                self.state = True
                return str(self.id) + ":" + str(self.x) + ":" + str(self.y) + ':' + 'COMPLETADO'

    def main(self):
        if self.api == 'N':
            self.registro(os.getenv("IP_REGISTRY"), int(os.getenv("PORT_REGISTRY")))
        else:
            self.registroApi(URL_REGISTRY)

        kafka = os.getenv('IP_ENGINE') + ':' + os.getenv('PORT_KAFKA')
        consumer = KafkaConsumer(
            'engine_drones',
            bootstrap_servers=[kafka],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: x.decode(FORMAT))

        producer = KafkaProducer(bootstrap_servers=[kafka])
        self.logearse(os.getenv("IP_ENGINE"), int(os.getenv("PORT_ENGINE")), producer, consumer)

if __name__ == "__main__":
    drone = AD_Drone()
    drone.main()
