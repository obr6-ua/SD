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
            
            conn.send((str(posx) + ":" + str(posy)).encode(FORMAT))
            
            # Verificar si ya hay una ID en la posición 0
            if self.mapa[1][1]:
                # Si ya hay una ID, la concatenamos con la nueva ID utilizando "/"
                self.mapa[1][1] += f"/\x1b[31m" + id + "\x1b[0m"
            else:
                 # Si no hay una ID en la posición 0, simplemente asignamos la nueva ID en rojo
                self.mapa[1][1] = f"\x1b[31m" + id + "\x1b[0m"

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
        self.sckServidor.bind((self.ipEngine, int(self.puerto_escucha)))
        self.sckServidor.listen(20)

        print("AD_Engine a la espera de que los drones se conecten.")
        print("Drones necesarios: " + str(self.dronesNecesarios))

        try:
            while len(self.idsValidas) < 2: #self.dronesNecesarios:
                CONEX_ACTIVAS = threading.active_count() - 3  # Obtén el número actual de hilos activos
                print("self.idsValidas " + str(len(self.idsValidas)))

                if CONEX_ACTIVAS <= self.dronesNecesarios:
                    conn, addr = self.sckServidor.accept()
                    thread = threading.Thread(target=self.manageDrone, args=(conn, addr, figuraActual))
                    thread.start()
                    time.sleep(3)
                else:
                    print("OOppsss... DEMASIADAS CONEXIONES. ESPERANDO A QUE ALGUIEN SE VAYA")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.sckServidor.close()
            print("Servidor cerrado")
    
    def printMap(self):
        print("   ", end="")
        for j in range(1, KTAMANYO + 1):
            print(f"{j:1}", end=" ")
        print()

        # Imprimir la matriz con los números de fila en el borde izquierdo
        for i in range(1, KTAMANYO):
            # Imprimir el número de fila en el borde izquierdo
            print(f"{i:1} ", end="")

            # Imprimir espacio en blanco en lugar de los valores de la matriz
            for j in range(1, KTAMANYO):
                elemento = self.mapa[j][i]
                print(f"{elemento:1}", end=" ")
            print()

    def updateMap(self, id, p_posx, p_posy, mov):
        print("Actualizando", flush=True)
        posx = int(p_posx)
        posy = int(p_posy)

        id_str = "\033[91m" + str(id) + "\033[0m"

        # Borra la posición anterior
        if mov == 'S' and posy > 1:
            self.mapa[posx][posy - 1] = ""
        elif mov == 'N' and posy < KTAMANYO - 1:
            self.mapa[posx][posy + 1] = ""
        elif mov == 'W' and posx < KTAMANYO - 1:
            self.mapa[posx + 1][posy] = ""
        elif mov == 'E' and posx > 1:
            self.mapa[posx - 1][posy] = ""

        print("Actualizando2", flush=True)

        # Verifica si la nueva posición está vacía y coloca el ID del dron
        if mov == 'S' and posy > 1 and self.mapa[posx][posy - 1] == "":
            self.mapa[posx][posy] = id_str
        elif mov == 'N' and posy < KTAMANYO - 1 and self.mapa[posx][posy + 1] == "":
            self.mapa[posx][posy] = id_str
        elif mov == 'W' and posx < KTAMANYO - 1 and self.mapa[posx + 1][posy] == "":
            self.mapa[posx][posy] = id_str
        elif mov == 'E' and posx > 1 and self.mapa[posx - 1][posy] == "":
            self.mapa[posx][posy] = id_str


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
        
        # Nos conectamos al server del clima
        #self.sckClima.connect((self.ipClima, int(self.puertoClima)))
        #temperatura = int(self.sckClima.recv(4096).decode('utf-8'))
        #self.sckClima.close()
        # Mostrar mapa
        self.printMap()
        time.sleep(1)
        mapa_serializado = [[str(item) for item in row] for row in self.mapa]

        temperatura = 1
        
        #matriz_serializada = json.dumps(mapa_serializado)
        # Mandar mapa por kafka
        producer.send(self.topicProductor, value=mapa_serializado) #matriz_serializada
        print("Mapa mandado por Kafka")
        valor = None
        # Recibir mensajes kafka
        while True:
            id, posx, posy, mov = "", "", "", ""
            if drones_completados == self.dronesNecesarios:
                self.printMap()
                print("COMPLETADO")
                self.sckClima.close()
                break
            if temperatura <= 0:
                    self.printMap()
                    print("CONDICIONES CLIMATICAS ADVERSAS. ESPECTACULO FINALIZADO")
                    self.sckClima.close()
                    self.salir()
            #self.sckClima.connect((self.ipClima, int(self.puertoClima)))
            for _, messages in consumer.poll(timeout_ms=1000).items():
                for message in messages:
                    valor = message.value.decode(FORMAT)  # Obtiene el valor del mensaje
                    print(valor)
                    break
            time.sleep(1)
            # Divide el mensaje "id:posx:posy:mov"
            if valor != None:
                id, posx, posy, mov = valor.split(":")
                if mov == "COMPLETADO":
                    print("self.mapa[int(posx)][int(posy)]  " + str(self.mapa[int(posx)][int(posy)]))
                    self.mapa[int(posx)][int(posy)] = "\033[92m" + str(id) + "\033[0m"
                    self.printMap()
                    drones_completados += 1
                    print("drones_completados " + str(drones_completados))
                else:
                    print(id + " " + mov)
                    # Actualizar mapa
                    self.updateMap(id, posx, posy, mov)
                    print("Actualizado", flush=True)
                    self.printMap()   
                    #temperatura = int(self.sckClima.recv(4096).decode('utf-8'))
                    #print(temperatura)   
            valor = None
            print("Mando mapa otra vez", flush=True)
            mapa_serializado = [[str(item) for item in row] for row in self.mapa]
            producer.send(self.topicProductor, value=mapa_serializado) 
            print("Mandado", flush=True)
            

    def nuevoEspectaculo(self):
        print("Hilos activos:")
        for thread in threading.enumerate():
            print(thread.ident, thread.name)
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

        while True:
            # Cuantos drones necesita la figura a realizar
            for figura in self.figuras:
                if figura["Completada"] == False:
                    self.dronesNecesarios = len(figura["Drones"])
                    figuraActual = figura

                    # Conectar nuevos drones
                    self.conectarDrones(figuraActual)

                    # Empezar a mandar y recibir mensajes por kafka
                    self.startKafka()
                    
                    figura["Completada"] = True
                else:
                    os.sleep(10)
                    print("No hay mas figuras, mandando drones a base")
                    self.mapa[0][0] = "/".join([f"\x1b[31m" + str(id) + "\x1b[0m" for id in self.idsValidas])
                    self.printMap()
                    self.start()
    
    def salir(self):
        print("Saliendo del espectaculo...")
        time.sleep(5)
        sys.exit(1)

    def cargarEspectaculo(self):
        print("Recuperando datos del espectaculo anterior...")
        time.sleep(5)
        print("Datos recuperados.")
        # Empezar a mandar y recibir mensajes por kafka
        self.startKafka()

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
                self.cargarEspectaculo()
            elif opcion == 3:
                self.salir()
            else:
                print("Opcion no valida, elige una opcion.")
        

def main():
    AD_Engine()

if __name__ == "__main__":
    main()
