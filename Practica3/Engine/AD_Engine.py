import re
import sys
import os
import time
import json
import socket
import threading
from datetime import datetime
import requests
from pymongo import MongoClient
from cryptography.fernet import Fernet
from kafka import KafkaConsumer, KafkaProducer
from prettytable import PrettyTable

API_KEY = 'e45bbc8bfead4e3311fdac9a7e9dd78c'

JSON = "AwD_figuras.json"
KTAMANYO = 20
FORMAT = 'utf-8'
clave_encriptada = os.getenv('CLAVE_ENCRIPTADA').encode()
cipher_suite = Fernet(clave_encriptada)

def escribir_log(mensaje, nombre_archivo="LogEngine"):
    with open(f"{nombre_archivo}.log", "a") as archivo_log:
        archivo_log.write(mensaje + "\n")

# Función para limpiar caracteres ANSI
def limpiar_ansi(texto):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', texto)

def encriptar_mensaje(mensaje):
    if isinstance(mensaje, str):
        mensaje_bytes = mensaje.encode(FORMAT)
    else:
        mensaje_bytes = mensaje  # Asume que ya es bytes
    mensaje_encriptado = cipher_suite.encrypt(mensaje_bytes)  # Encriptar
    return mensaje_encriptado

def desencriptar_mensaje(mensaje_encriptado):
    mensaje_desencriptado = cipher_suite.decrypt(mensaje_encriptado)  # Desencriptar
    return mensaje_desencriptado.decode(FORMAT)

class Figuras:
    def __init__(self, JSON):
        self.listaFiguras = self.leer_desde_json(JSON)

    def leer_desde_json(self, JSON):
        with open(JSON, "r") as archivo_json:
            datos = json.load(archivo_json)

        self.listaFiguras = []

        for figura_json in datos.get("figuras"):
            nombre_figura = figura_json.get("Nombre")
            drones_json = figura_json.get("Drones")

            self.drones_lista = []

            for drone_json in drones_json:
                id_drone = drone_json.get("ID")
                posicion_x, posicion_y = map(int, drone_json.get("POS").split(','))

                self.drones_lista.append({"ID": id_drone, "Posicion X": posicion_x, "Posicion Y": posicion_y})

            figura = {"Nombre": nombre_figura, "Drones": self.drones_lista, "Completada": False}
            self.listaFiguras.append(figura)

        return self.listaFiguras

class AD_Engine:
    def __init__(self):
        self.puerto_escucha = os.getenv('PUERTO_ESCUCHA')
        self.conexionBBDD = "mongodb://" + os.getenv('IP_BBDD') + ":" + os.getenv('PUERTO_BBDD')
        self.boostrap_server = os.getenv('IP_SERVER_GESTOR') + ":" + os.getenv('PUERTO_SERVER_GESTOR')
        self.topicConsumidor = os.getenv('TOPIC_CONSUMIDOR')
        self.topicProductor =  os.getenv('TOPIC_PRODUCTOR')
        self.ipEngine = os.getenv('IP_ENGINE')
        self.idsValidas = []
        self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]
        self.figuras = []
        self.lock = threading.Lock()

        self.cliente = MongoClient(self.conexionBBDD)
        self.bd = self.cliente['drones_db']
        self.coleccion1 = self.bd['drones']

        try:
            info = self.cliente.server_info()
            escribir_log("Conexión exitosa a MongoDB")
        except Exception:
            escribir_log("No se pudo conectar a MongoDB. Verifica la configuración de conexión.")

        self.start()

    def MapaADiccionario(self):
        mapa_dict = {}
        for i in range(KTAMANYO):
            for j in range(KTAMANYO):
                key = f"{i},{j}"
                mapa_dict[key] = self.mapa[i][j]
        return mapa_dict

    def actualizarMapaDB(self):
        mapa_dict = self.MapaADiccionario()
        self.bd.mapa.update_one({'_id': 'ID_MAPA'}, {'$set': {'mapa': mapa_dict}}, upsert=True)

    def manageDrone(self, conn, addr, figuraActual):
        escribir_log(f"Nuevo dron {addr} conectado. {datetime.now()}")
        token = desencriptar_mensaje(conn.recv(4096))
        escribir_log(f"Comprobando token {addr}. {datetime.now()}")
        print(token)

        registro = self.coleccion1.find_one({"token": token})
        print(f"Encontrado {registro['hora']}")

        print(datetime.now())
        if registro['hora'] < datetime.now():
            print("Token valido")
            escribir_log(f"Token expirado {addr}. {datetime.now()}")
            conn.close()
        else:
            if registro:
                id = registro['id']
                print("ID RECUPERADO " + str(id))
                primer_dron = figuraActual["Drones"].pop(0)
                posx = primer_dron.get("Posicion X", None)
                posy = primer_dron.get("Posicion Y", None)
                escribir_log(f"Nuevo dron ID:{id} conectado. {datetime.now()}")
                print('Mensaje: ' + str(posx) + ":" + str(posy))

                conn.send(encriptar_mensaje(f"{posx}:{posy}"))

                if self.mapa[1][1]:
                    self.mapa[1][1] += "|\033[91m" + id +"\033[0m"
                else:
                    self.mapa[1][1] = "\033[91m" + id + "\033[0m"

                with self.lock:
                    self.idsValidas.append(id)
                conn.close()
            else:
                print("No se encontró ningún registro para el dron con ID y token especificados")
                print("FIN")
                conn.close()

    def conectarDrones(self, figuraActual):
        self.sckServidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sckServidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sckServidor.bind((self.ipEngine, int(self.puerto_escucha)))
        self.sckServidor.listen(20)

        print("AD_Engine a la espera de que los drones se conecten.")
        print("Drones necesarios: " + str(self.dronesNecesarios))

        print(figuraActual['Nombre'])
        try:
            while len(self.idsValidas) < self.dronesNecesarios:
                print("self.idsValidas " + str(len(self.idsValidas)))

                conn, addr = self.sckServidor.accept()
                self.manageDrone(conn, addr, figuraActual)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.sckServidor.close()
            print("Servidor cerrado")

    def printMap(self):
        table = PrettyTable()
        header = [""] + [str(j) for j in range(1, KTAMANYO)]
        table.field_names = header

        for i in range(1, KTAMANYO):
            row = [str(i)] + [self.mapa[j][i] for j in range(1, KTAMANYO)]
            table.add_row(row)

        print(table)

    def enviar_actualizacion_frontend(self):
        try:
            mapa_serializado = [[{"id": limpiar_ansi(item.strip('\033[91m\033[92m\033[0m')), "completado": "\033[92m" in item} for item in row] for row in self.mapa]
            response = requests.post("http://192.168.18.32:5000/update", json=mapa_serializado)
            if response.status_code == 200:
                print("Actualización enviada al frontend")
            else:
                print(f"Error al enviar la actualización al frontend: {response.status_code}")
        except Exception as e:
            escribir_log(f"Error al enviar la actualización al frontend: {e}")

    def updateMap(self, id, p_posx, p_posy, mov):
        new_posx = int(p_posx)
        new_posy = int(p_posy)
        id_str = "\033[91m" + str(id) + "\033[0m"
        old_posx, old_posy = new_posx, new_posy

        if mov == 'N':
            old_posy += 1
        elif mov == 'S':
            old_posy -= 1
        elif mov == 'E':
            old_posx -= 1
        elif mov == 'W':
            old_posx += 1
        elif mov == 'COMPLETADO':
            self.mapa[new_posx][new_posy] = "\033[92m" + str(id) + "\033[0m"
            self.enviar_actualizacion_frontend()
            return

        pos_anterior = self.mapa[old_posx][old_posy]
        if pos_anterior:
            drones = pos_anterior.split("|")
            if id_str in drones:
                drones.remove(id_str)
                self.mapa[old_posx][old_posy] = "|".join(drones).strip()

        if self.mapa[new_posx][new_posy] != "":
            self.mapa[new_posx][new_posy] += "|" + id_str
        else:
            self.mapa[new_posx][new_posy] = id_str

        self.enviar_actualizacion_frontend()

    def startKafka(self):
        consumer = KafkaConsumer(
            self.topicConsumidor,
            bootstrap_servers=[self.boostrap_server],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='engine')

        producer = KafkaProducer(bootstrap_servers=[self.boostrap_server], value_serializer=lambda x: x)
        self.printMap()
        time.sleep(0.1)

        for figura in self.figuras:
            if figura["Completada"] == False:
                self.dronesNecesarios = len(figura["Drones"])
                figuraActual = figura
                self.conectarDrones(figuraActual)
                self.actualizarMapaDB()

                try:
                    with open('ciudad.txt', 'r') as archivo:
                        ciudad_elegida = archivo.read().strip()
                except FileNotFoundError:
                    print("El archivo ciudad.txt no se encuentra.")
                    escribir_log("El archivo ciudad.txt no se encuentra.")
                    return

                url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad_elegida}&appid={API_KEY}"
                respuesta = requests.get(url)
                if respuesta.status_code == 200:
                    data = respuesta.json()
                    temperatura = round(data["main"]["temp"] - 273.15)
                    escribir_log("Temperatura recuperada")

                try:
                    mapa_serializado = [[str(item) for item in row] for row in self.mapa]
                    mapa_json = json.dumps(mapa_serializado)
                    mensaje_encriptado = encriptar_mensaje(mapa_json)
                    producer.send(self.topicProductor, value=mensaje_encriptado)
                    escribir_log("Mapa mandado por Kafka")
                except Exception as e:
                    print(f"Error al enviar el mapa por Kafka: {e}")
                    escribir_log(f"Error al enviar el mapa por Kafka: {e}")
                    return

                self.figura(temperatura, consumer, producer)
                figura["Completada"] = True

                self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]
                self.idsValidas = []

        producer.send(self.topicProductor, value=encriptar_mensaje('FIN'))

    def figura(self, temperatura, consumer, producer):
        id, posx, posy, mov = "", "", "", ""
        drones_completados = 0

        while True:
            print("Temperatura: " + str(temperatura))

            if drones_completados == self.dronesNecesarios:
                self.printMap()
                time.sleep(3)
                producer.send(self.topicProductor, value=encriptar_mensaje('RESET'))
                print("COMPLETADO")
                return
            if temperatura <= 0:
                self.printMap()
                producer.send(self.topicProductor, value=encriptar_mensaje('CANCELAR'))
                self.salir()

            for message in consumer:
                valor = desencriptar_mensaje(message.value)
                id, posx, posy, mov = valor.split(":")
                if mov == "COMPLETADO":
                    drones_completados += 1
                    self.updateMap(id, posx, posy, mov)
                    self.printMap()
                    mapa_serializado = [[str(item) for item in row] for row in self.mapa]
                    producer.send(self.topicProductor, value=encriptar_mensaje(json.dumps(mapa_serializado)))
                    break
                else:
                    self.updateMap(id, posx, posy, mov)
                    mapa_serializado = [[str(item) for item in row] for row in self.mapa]
                    producer.send(self.topicProductor, value=encriptar_mensaje(json.dumps(mapa_serializado)))
                    self.printMap()
                    break
            time.sleep(0.1)

    def nuevoEspectaculo(self):
        for figura in self.figuras:
            figura["Completada"] = False

        self.idsValidas.clear()
        self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]

        while True:
            if os.path.exists(JSON) and os.path.getsize(JSON) > 0:
                break
            print(f"Esperando a que el archivo {JSON} contenga datos...")
            time.sleep(1)

        print(f"El archivo {JSON} contiene datos. Procesando...")

        self.figuras = Figuras(JSON).listaFiguras

        print(f"El archivo {JSON} ha sido procesado.")

        self.startKafka()

    def salir(self):
        print("Saliendo del espectaculo...")
        time.sleep(5)
        sys.exit(1)

    def menu(self):
        print("AD_ENGINE MENU PRINCIPAL")
        print("Elige una opcion:")
        print("1. Nuevo espectaculo")
        print("2. Cargar ultimo espectaculo")
        print("3. Salir")
        opcion = input("Ingresa el número de la opción que deseas: ")
        return int(opcion)

    def start(self):
        opcion = -1
        while opcion not in (1,2,3):
            opcion = self.menu()
            if opcion == 1:
                self.nuevoEspectaculo()
            elif opcion == 2:
                self.salir()
            else:
                print("Opcion no valida, elige una opcion.")

def main():
    AD_Engine()

if __name__ == "__main__":
    main()
