from kafka import KafkaConsumer, KafkaProducer
from multiprocessing import Process
from json import loads

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


    def editUser(self,host, port):
        ADDR_REGISTRO = (host, port)
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR_REGISTRO)
            print (f"Establecida conexión en [{ADDR_REGISTRO}]")

            alias = input("Alias antiguo: ")

            cadena = "1:"+self.id+":"+alias
            
            client.send(str(cadena).encode(FORMAT))

            self.alias = client.recv(HEADER).encode(FORMAT)
                
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

            
            cadena = "1:"+self.id+":"+self.alias

            client.send(cadena.encode(FORMAT)) 

            token = client.recv(HEADER).decode(FORMAT) 

            print(f"He recibido el mensaje del Registry: {token}")
            
            
            return 

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
            group_id='drones')

        # Creamos productor
        self.producer = KafkaProducer(bootstrap_servers=[kafka])

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


    def logearse(self ,host, port):
        ADDR_log = (host, port) 
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(ADDR_log)
        except:
            print("El servidor está desconectado o ya hay una partida en curso")
            client.close()
            return

        print (f"Establecida conexión en [{ADDR_log}]")
  
        client.send(self.token.encode(FORMAT))

        recibido = client.recv(HEADER).decode(FORMAT)
        
        recibido.split(':')
        
        self.finalx = recibido[0]
        self.finaly = recibido[1]
        
        self.iniciarKafka()
        
        
        while(self.state != True):  
            self.mapa = loads(self.consumer.value.decode('utf-8'))
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
                self.editUser(os.getenv("IP"), int(os.getenv("PORT")))
            elif res == "2": 
                dron = self.registro(os.getenv("IP"), int(os.getenv("PORT")))
                #Opcion 2 se conecta por sockets al registry
            elif res == "3":
                #Por sockets se conectan al engine pasandole alias + password
                self.logearse(os.getenv("IP_ENGINE") , int(os.getenv("PORT_ENGINE")) , dron)
            elif res == "4":
                ""
                # alias = input("¿Cuál era tu alias?: ")
                # iniciarKafka(alias)



if __name__ == "__main__":
    AD_Drone.main()
