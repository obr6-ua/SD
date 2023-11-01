import sys
import os
import time
import json
import socket
import threading
import keyboard
from pymongo import MongoClient
from kafka import KafkaConsumer
from kafka import KafkaProducer
#from json import loads

JSON = "AwD_figuras.json"

# La clase Figuras almacena los datos de las figuras llegados desde el JSON
class Figuras:
    def __init__(self, archivo):
        self.completada = False
        self.listaFiguras = self.leer_desde_json(archivo)

    def leer_desde_json(self, archivo):
        with open(archivo, "r") as archivo_json:
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

            figura = {"Nombre": nombre_figura, "Drones": self.drones_lista}
            self.listaFiguras.append(figura)

        return self.listaFiguras

class AD_Engine:

    def __init__(self):
        self.puerto_escucha = os.getenv('PUERTO_ESCUCHA')
        self.conexionBBDD = os.getenv('IP_BBDD') + ":" + os.getenv('PUERTO_BBDD')
        self.boostrap_server = os.getenv('IP_SERVER_GESTOR') + ":" +os.getenv('PUERTO_SERVER_GESTOR')
        self.topicConsumidor = os.getenv('TOPIC_CONSUMIDOR')
        self.topicProductor =  os.getenv('TOPIC_PRODUCROR')
        self.ipEngine = os.getenv('IP_ENGINE')
        self.idsValidas = []
        # Creamos mapa 20x20 vacio
        self.mapa = [["" for _ in range(20)] for _ in range(20)]

        # Inicializamos la base de datos
        cliente = MongoClient(self.conexionBBDD)
        self.bd = self.cliente['AWD']
        self.coleccion1 = self.bd['ID-TOKEN']
        
        # Creamos consumidor
        self.consumer = KafkaConsumer(
        'drones_engine',
        bootstrap_servers=[self.boostrap_server],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='engine')

        # Creamos productor
        self.producer = KafkaProducer(bootstrap_servers=[self.boostrap_server])

        self.start()
    
    def manageDrone(self, conn, addr):
        print(f"Nuevo dron {addr} conectado.")
        while True:
            msg_length = conn.recv(4096)
            if msg_length:
                msg_length = int(msg_length)
                
                # Mensaje del tipo "id:token"
                msg = conn.recv(msg_length)
                aux = msg.split(":")
                id = aux[0]
                token = aux[1]

                # Buscamos ese token en la bbdd
                registro = self.coleccion1.find_one({"ID": id, "token": token})

                if registro:
                    print("ID y Token validos")

                    # Le mandamos al dron posicion x e y asignadas
                    for figura in self.figuras:
                        if figura.completada == False:
                            primer_dron = figura.drones_lista.pop(0)
                            posx = primer_dron.get("Posicion X", None) 
                            posy = primer_dron.get("Posicion Y", None)
                    conn.send(posx + ":" + posy)

                    # Me guardo el id del dron que ha logrado registrarse correctamente
                    self.idsValidas.append(id)
                    conn.close()

                else:
                    print("No se encontró ningún registro para el dron con ID y token especificados")
                    conn.send("FIN")
                    conn.close()
    
    def conectarDrones(self, figuras):
        self.sckServidor=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sckServidor.bind((self.ipEngine, self.puerto_escucha))
        self.sckServidor.listen(20)
        CONEX_ACTIVAS = threading.active_count()-1

        # Cuantos drones necesita la figura a realizar
        for figura in figuras:
            if figura.completada == False:
                self.dronesNecesarios = len(figura.drones_lista)

        while True:
            conn, addr = self.sckServidor.accept()
            CONEX_ACTIVAS = threading.active_count()

            if (CONEX_ACTIVAS <= self.dronesNecesarios): 
                thread = threading.Thread(target=self.manageDrone, args=(conn, addr))
                thread.start()
    
            else:
                print("OOppsss... DEMASIADAS CONEXIONES. ESPERANDO A QUE ALGUIEN SE VAYA")
                conn.send("OOppsss... DEMASIADAS CONEXIONES. Tendrás que esperar a que alguien se vaya")
                conn.close()
                CONEX_ACTUALES = threading.active_count()-1

    def nuevoEspectaculo(self):
        while True:
            # Verifica si la tecla Escape (Esc) ha sido presionada
            if keyboard.is_pressed('esc') == 0:
                # Reseteo informacion guardada
                # Pongo todas las figuras sin completar
                for figura in self.figuras:
                    figura.estado = False
                
                # Borro los datos de registro de los drones de bbdd
                self.coleccion1.delete_many({})

                # Borro registro de ids validas
                self.idsValidas.clear()
                
                # Almacenamos datos de las figuras
                while True:
                    if os.path.exists(JSON) and os.path.getsize(JSON) > 0:
                        break
                    print(f"Esperando a que el archivo {JSON} contenga datos...")
                    time.sleep(1)

                print(f"El archivo {JSON} contiene datos. Procesando...")

                self.figuras = Figuras(JSON).listaFiguras

                # Conectar nuevos drones
                self.conectarDrones(self.figuras)

                # Poner todas las ids en la posicion 0
                self.mapa[0][0] = "/".join([f"\x1b[31m{id}\x1b[0m" for id in self.idsValidas])

                while True:
                    # Mostrar mapa

                    # Mandar mapa por kafka

                    # Recibir mensajes kafka

            else:
                print("Tecla Escape presionada. Saliendo del espectaculo.")
                self.menu()


    def menu(self):
        print("AD_ENGINE MENU PRINCIPAL")
        print("Elige una opcion:")
        print("1. Nuevo espectaculo (para salir pulsa esc)")
        print("2. Cargar ultimo espectaculo")
        print("3. Salir")
        opcion = input("Ingresa el número de la opción que deseas: ")
        return int(opcion)

    def start(self):
        opcion = self.menu()

        if opcion == 1:
            self.nuevoEspectaculo()
           
        

def main():
    args = sys.argv
    engine = AD_Engine()

if __name__ == "__main__":
    main()
