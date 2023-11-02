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
from random import randint
#from json import loads

JSON = "AwD_figuras.json"
KTAMANYO = 20

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
        self.ipClima = os.getenv('IP_CLIMA')
        self.puertoClima = os.getenv('PUERTO_CLIMA')
        self.idsValidas = []
        # Creamos mapa 20x20 vacio
        self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]

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
        group_id='engine',
        value_serializer=lambda x: json.dumps(x).encode('utf-8'))

        # Creamos productor
        self.producer = KafkaProducer(bootstrap_servers=[self.boostrap_server], 
                                      value_serializer=lambda x: json.dumps(x).encode('utf-8'))
        
        # Cleamos el socket al servidor del clima
        self.sckClima = socket.socket()

        self.start()
    
    def manageDrone(self, conn, addr, figuraActual):
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
                    for dron in figuraActual.drones_lista:
                        primer_dron = dron.pop(0)
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
    
    def conectarDrones(self, figuraActual):
        self.sckServidor=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sckServidor.bind((self.ipEngine, self.puerto_escucha))
        self.sckServidor.listen(20)
        CONEX_ACTIVAS = threading.active_count()-1

        while True:
            conn, addr = self.sckServidor.accept()
            CONEX_ACTIVAS = threading.active_count()

            if (CONEX_ACTIVAS <= self.dronesNecesarios): 
                thread = threading.Thread(target=self.manageDrone, args=(conn, addr, figuraActual))
                thread.start()
    
            else:
                print("OOppsss... DEMASIADAS CONEXIONES. ESPERANDO A QUE ALGUIEN SE VAYA")
                conn.send("OOppsss... DEMASIADAS CONEXIONES. Tendrás que esperar a que alguien se vaya")
                conn.close()
                CONEX_ACTUALES = threading.active_count()-1
    
    def printMap(self):
        print("   ", end="")
        for j in range(1, KTAMANYO + 1):
            print(f"{j:4}", end=" ")
        print()

        # Imprimir la matriz con los números de fila en el borde izquierdo
        for i in range(1, KTAMANYO + 1):
            # Imprimir el número de fila en el borde izquierdo
            print(f"{i:3} ", end="")

            # Imprimir espacio en blanco en lugar de los valores de la matriz
            for _ in range(KTAMANYO):
                print(self.mapa[j][i])
            print()
    
    def buscarId(self, id):
        fila_encontrada = -1
        columna_encontrada = -1

        for fila, lista in enumerate(self.mapa):
            if id in lista:
                columna_encontrada = lista.index(self.mapa)
                fila_encontrada = fila
                break
        return columna_encontrada, fila_encontrada

    def updateMap(self, id, mov):
        posx, posy = self.buscarId(id)
        
        if mov == 'N':
            if self.mapa[posx][posy-1]:
                self.mapa[posx][posy-1] = self.mapa[posx][posy-1] + "/" + "\033[91m{id}\033[0m"
            self.mapa[posx][posy-1] = "\033[91m{id}\033[0m"
        elif mov == 'S':
            if self.mapa[posx][posy+1]:
                self.mapa[posx][posy+1] = self.mapa[posx][posy+1] + "/" + "\033[91m{id}\033[0m"
            self.mapa[posx][posy+1] = "\033[91m{id}\033[0m"
        elif mov == 'E':
            if self.mapa[posx-1][posy]:
                self.mapa[posx][posy-1] = self.mapa[posx][posy-1] + "/" + "\033[91m{id}\033[0m"
            self.mapa[posx][posy-1] = "\033[91m{id}\033[0m"
        else:
            if self.mapa[posx+1][posy]:
                self.mapa[posx][posy+1] = self.mapa[posx][posy+1] + "/" + "\033[91m{id}\033[0m"
            self.mapa[posx][posy+1] = "\033[91m{id}\033[0m"

    def startKafka(self):
        drones_completados = 0
        
        # Nos conectamos al server del clima
        self.sckClima.connect((self.ipClima, self.puertoClima))
        ciudad = self.sckClima.recv(4096).decode('utf-8')
        
        clima = randint(0, len(self.listaCiudades)-1)
        while drones_completados < self.idsValidas and ciudad["temperatura"] > 0:
            # Mostrar mapa
            self.printMap()
            # Mandar mapa por kafka
            self.producer.send(self.topicProductor, value=self.mapa)
            # Recibir mensajes kafka
            for mensaje in self.consumer:
                valor = mensaje.value  # Obtiene el valor del mensaje

                if valor == "id:COMPLETADO":
                    id, aux = valor.split(":")
                    posx, posy = self.buscarId(id)
                    self.mapa[posx][posy].replace("\033[91m{id}\033[0m", "\033[92m{id}\033[0m")
                    drones_completados += 1
                else:
                    # Divide el mensaje en "id" y "letra"
                    id, mov = valor.split(":")
                    # Actualizar mapa
                    self.updateMap(id, mov)
            ciudad = self.sckClima.recv(4096).decode('utf-8')
            if clima < 0:
                print("“CONDICIONES CLIMATICAS ADVERSAS. ESPECTACULO FINALIZADO")
                self.sckClima.close()
                self.salir()

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

                while True:
                    # Cuantos drones necesita la figura a realizar
                    for figura in self.figuras:
                        if figura.completada == False:
                            self.dronesNecesarios = len(figura.drones_lista)
                            figuraActual = figura

                            # Conectar nuevos drones
                            self.conectarDrones(figuraActual)

                            # Borrar mapa
                            self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]

                            # Poner todas las ids en la posicion 0
                            self.mapa[0][0] = "/".join([f"\x1b[31m{id}\x1b[0m" for id in self.idsValidas])

                            # Empezar a mandar y recibir mensajes por kafka
                            self.startKafka()
                            figura.completada = True
                        else:
                            os.sleep(10)
                            print("No hay mas figuras, mandando drones a base")
                            self.mapa[0][0] = "/".join([f"\x1b[31m{id}\x1b[0m" for id in self.idsValidas])
                            self.printMap()
                            self.start()
            else:
                print("Tecla Escape presionada. Saliendo del espectaculo.")
                self.start()
    
    def salir(self):
        print("Saliendo del espectaculo...")
        os.sleep(5)
        sys.exit(1)

    def cargarEspectaculo(self):
        print("Recuperando datos del espectaculo anterior...")
        os.sleep(5)
        print("Datos recuperados.")
        # Empezar a mandar y recibir mensajes por kafka
        self.startKafka()

    def menu(self):
        print("AD_ENGINE MENU PRINCIPAL")
        print("Elige una opcion:")
        print("1. Nuevo espectaculo (para salir pulsa esc)")
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
                self.cargarEspectaculo()
            elif opcion == 3:
                self.salir()
            else:
                print("Opcion no valida, elige una opcion.")
        

def main():
    engine = AD_Engine()

if __name__ == "__main__":
    main()
