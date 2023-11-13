import sys
import os
import time
import json
import socket
import threading
from pymongo import MongoClient
from kafka import KafkaConsumer
from kafka import KafkaProducer
from prettytable import PrettyTable
#from random import randint

JSON = "AwD_figuras.json"
KTAMANYO = 20
FORMAT = 'utf-8'


# La clase Figuras almacena los datos de las figuras llegados desde el JSON
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
        self.ipClima = os.getenv('IP_CLIMA')
        self.puertoClima = os.getenv('PUERTO_CLIMA')
        self.idsValidas = []
        # Creamos mapa 20x20 vacio
        self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]
        self.figuras = []
        self.lock = threading.Lock()

        # Inicializamos la base de datos   "mongodb://localhost:27017"
        self.cliente = MongoClient(self.conexionBBDD) #self.conexionBBDD
        self.bd = self.cliente['drones_db']
        self.coleccion1 = self.bd['drones']

        try:
            # Ejecuta una consulta de prueba
            info = self.cliente.server_info()
            print("Conexión exitosa a MongoDB")
            print("Versión de MongoDB:", info["version"])
            print()
        except Exception:
            print("No se pudo conectar a MongoDB. Verifica la configuración de conexión.")
            print()
        
        # Cleamos el socket al servidor del clima
        self.sckClima = socket.socket()

        self.start()
    
    def manageDrone(self, conn, addr, figuraActual):
        print(f"Nuevo dron {addr} conectado.")
        # Mensaje del dron a conectar
        token = conn.recv(4096).decode(FORMAT)
        
        print(token)
        
        # Buscamos ese token en la bbdd
        registro = self.coleccion1.find_one({"token": token})

        #Si existe pillamos los datos del dron
        if registro:
            id = registro['id'] 
            print("ID RECUPERADO " + str(id))
            # Le mandamos al dron posicion x e y asignadas
            primer_dron = figuraActual["Drones"].pop(0)
            posx = primer_dron.get("Posicion X", None) 
            posy = primer_dron.get("Posicion Y", None)
            
            print('Mensaje: ' + str(posx) + ":" + str(posy))
            
            conn.send((str(posx) + ":" + str(posy)).encode(FORMAT))
            
            # Verificar si ya hay una ID en la posición 0
            if self.mapa[1][1]:
                # Si ya hay una ID, la concatenamos con la nueva ID utilizando "/"
                self.mapa[1][1] += "|\033[91m" + id +"\033[0m"
            else:
                 # Si no hay una ID en la posición 0, simplemente asignamos la nueva ID en rojo
                self.mapa[1][1] = "\033[91m" + id + "\033[0m"

            # Me guardo el id del dron que ha logrado registrarse correctamente
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

        threads = []
        
        print(figuraActual['Nombre'])    
        try:
            while len(self.idsValidas) < self.dronesNecesarios:
                print("self.idsValidas " + str(len(self.idsValidas)))

                conn, addr = self.sckServidor.accept()
                self.manageDrone(conn, addr, figuraActual)
                #time.sleep(0.3)
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

    def updateMap(self, id, p_posx, p_posy, mov):
        # Convertir a enteros las posiciones
        new_posx = int(p_posx)
        new_posy = int(p_posy)

        # Formato de ID del dron
        id_str = "\033[91m" + str(id) + "\033[0m"

        # Determinar la posición anterior basada en el movimiento
        old_posx, old_posy = new_posx, new_posy
        if mov == 'N':
            old_posy += 1
        elif mov == 'S':
            old_posy -= 1
        elif mov == 'E':
            old_posx -= 1
        elif mov == 'W':
            old_posx += 1

        # Borrar el ID del dron de la posición anterior
        pos_anterior = self.mapa[old_posx][old_posy]
        if pos_anterior:
            print(pos_anterior)
            drones = pos_anterior.split("|")
            if id_str in drones:
                drones.remove(id_str)
                self.mapa[old_posx][old_posy] = "|".join(drones).strip()

        # Verificar si la nueva posición ya tiene un dron
        if self.mapa[new_posx][new_posy] != "":
            # Concatenar los IDs de los drones
            self.mapa[new_posx][new_posy] += "|" + id_str
        else:
            # Colocar el dron en la nueva posición
            self.mapa[new_posx][new_posy] = id_str


    def startKafka(self):
        drones_completados = 0

        # Creamos consumidor
        consumer = KafkaConsumer(
            self.topicConsumidor,
            bootstrap_servers=[self.boostrap_server],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='engine')

        # Creamos productor
        producer = KafkaProducer(bootstrap_servers=[self.boostrap_server],value_serializer=lambda x: 
                         json.dumps(x).encode('utf-8'))
        
        
        # Mostrar mapa
        self.printMap()
        time.sleep(1)
        mapa_serializado = [[str(item) for item in row] for row in self.mapa]

        # Mandar mapa por kafka
        producer.send(self.topicProductor, value=mapa_serializado)
        print("Mapa mandado por Kafka")
        valor = None
        # Recibir mensajes kafka
        for figura in self.figuras:
            if figura["Completada"] == False:
                self.dronesNecesarios = len(figura["Drones"])
                figuraActual = figura
                temperatura=1
                # Conectar nuevos drones
                self.conectarDrones(figuraActual)
                # Nos conectamos al server del clima
                # self.sckClima.connect((self.ipClima, int(self.puertoClima)))
                # temperatura = int(self.sckClima.recv(4096).decode('utf-8'))
                # self.sckClima.close()
                self.figura(temperatura, consumer, producer)             
                
                figura["Completada"] = True
                
                #Reseteamos los campos necesarios
                self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]
                self.idsValidas = []
                
        #Enviamos a los drones que todas las figuras han sido terminadas
        producer.send(self.topicProductor, value='FIN')

            
    def figura(self , temperatura , consumer , producer):
        id, posx, posy, mov = "", "", "", ""
        drones_completados = 0
        consumidos = 0
        consumos = self.dronesNecesarios
        while True:
            if drones_completados == self.dronesNecesarios:
                self.printMap()
                time.sleep(5)
                producer.send(self.topicProductor, value='RESET')
                print("COMPLETADO")
                
                return
            if temperatura <= 0:
                    self.printMap()
                    producer.send(self.topicProductor, value='CANCELAR')
                    self.sckClima.close()
                    self.salir()
            
            #self.sckClima.connect((self.ipClima, int(self.puertoClima)))
            for message in consumer:
                valor = message.value.decode(FORMAT)  # Obtiene el valor del mensaje
                id, posx, posy, mov = valor.split(":")
                if mov == "COMPLETADO":
                    print(f'Consumidos: = {consumidos}')
                    drones_completados += 1
                    print(f'Consumos: = {consumos}')
                    print("self.mapa[int(posx)][int(posy)]  " + str(self.mapa[int(posx)][int(posy)]))
                    self.mapa[int(posx)][int(posy)] = "\033[92m" + str(id) + "\033[0m"
                    self.updateMap(id, posx, posy, mov)
                    self.printMap()
                    mapa_serializado = [[str(item) for item in row] for row in self.mapa]
                    producer.send(self.topicProductor, value=mapa_serializado)
                    
                    break
                else:
                    print(id + " " + mov)
                    # Actualizar mapa
                    self.updateMap(id, posx, posy, mov)
                    mapa_serializado = [[str(item) for item in row] for row in self.mapa]
                    producer.send(self.topicProductor, value=mapa_serializado)     
                    self.printMap()
                    print("Actualizado", flush=True)
                    #temperatura = int(self.sckClima.recv(4096).decode('utf-8'))  
                    break
            time.sleep(0.1)

    def nuevoEspectaculo(self):
        # Reseteo informacion guardada
        # Pongo todas las figuras sin completar
        for figura in self.figuras:
            figura["Completada"] = False
            
        # Borro los datos de registro de los drones de bbdd
        # self.coleccion1.delete_many({})

        # Borro registro de ids validas
        self.idsValidas.clear()

        # Borrar mapa
        self.mapa = [["" for _ in range(KTAMANYO)] for _ in range(KTAMANYO)]
            
        # Almacenamos datos de las figuras
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
