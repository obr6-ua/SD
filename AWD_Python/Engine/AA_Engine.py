from multiprocessing import Process, Manager
from random import randint
from colorama import Fore
from kafka import KafkaProducer, KafkaConsumer
from NucleoDB import NucleoDB
from Utils import *

import socket
import sys
import threading
import os
import time

FORMAT = 'utf-8'
HEADER = 128

if(os.getenv('entorno') == None):
    IP = os.getenv
    SERVER_CLIMA  = '0.0.0.0'
    SERVER_NUCLEO = '0.0.0.0'
    SERVER_KAFKA  = 'localhost'
else:
    SERVER_CLIMA  = '10.0.0.2'
    SERVER_NUCLEO = '10.0.0.3'
    SERVER_KAFKA  = '10.0.0.5'

class Engine:
    def __init__(self,mode):
        #Base de datos
        self.db = NucleoDB()
        #Recursos compartidos para procesos
        manager = Manager()
        self.conexiones = manager.list()

        if(mode == 1):
            self.juegoNuevo()
        elif(mode == 2):
            self.recuperarPartidaBD()

    def iniciarKafka(self):
        mapTopic = 'map'
        movTopic = 'moves'
        try:
            mapProducer = KafkaProducer(bootstrap_servers=SERVER_KAFKA)
            movConsumer = KafkaConsumer(movTopic,bootstrap_servers=SERVER_KAFKA)

            mapProducer.send(mapTopic, self.dibujarMapa().encode(FORMAT))
            mapProducer.flush()
        except:
            print("Fallo con el servidor de kafka")
            return
            
        print("Enviada primera instancia del mapa")

        for mov in movConsumer:
            print("Movimiento entrante")
            info = eval(mov.value.decode(FORMAT))
            alias = info[0]
            movimiento = info[1]
            print(f"{alias} ha hecho el movimiento {movimiento}")

            self.moverdron(dron, movimiento)
            self.db.insertarMapa(str(self.mapa))

            try:   
                if(True):
                    mapProducer.send(mapTopic, f'FIN DE PARTIDA'.encode(FORMAT))
                    sys.exit(0)
                else:
                    mapProducer.send(mapTopic, self.dibujarMapa().encode(FORMAT))
            except:
                print("Fallo con el servidor de kafka")
                return

    def juegoNuevo(self):

        #Argumentos
        args = sys.argv
        args.pop(0)
        if(comprobarArgs(args, "engine") == False): sys.exit(-1)

        #Mapa, ciudades y drones
        self.mapa      = self.generarMapa()
        self.ciudades  = obtenerCiudades(SERVER_CLIMA, self.AA_weather_port)
        self.drones = []

        #Base de datos
        self.db.borrarAll()
        self.db.crearAll()


        self.esperardrones()

        self.db.insertarMapa(str(self.mapa))
        self.db.insertarCiudades(self.ciudades)


    def recuperarPartidaBD(self):
        #Mapa
        aux = self.db.leer("mapa").pop()
        self.mapa = eval(aux[1])

        #Ciudades
        self.ciudades = []
        aux = self.db.leer("ciudades")

        for ciudad in aux:
            self.ciudades.append({"ciudad" : ciudad[0], "temperatura" : ciudad[1]})

        #drones
        self.drones = []
        aux = self.db.leer("drones")

        for dron in aux:
            alias = dron[0]
            pos   = eval(dron[1])
            estado = dron[2]
            
    
    ## Función que genera 3 procesos
    ## procesoLogin: proceso principal encargado de escuchar las peticiones de login de los drones
    ## procesoEnter: proceso encargado de leer un input (enter). Si se pulsa el enter, se para la escucha y se inicia el juego
    ## procesoStatus: comprueba que se haya alcanzado el límite de drones
    def esperardrones(self):
        print("Iniciando procesos para esperar drones")
        print("Pulsa enter para parar la escucha del servidor e iniciar la partida")
        
        server = SERVER_NUCLEO
        loginSoket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        loginSoket.bind((server, self.port))
        loginSoket.listen()
        print(f"Servidor login escuchando en {server} {self.port}")

        fn = sys.stdin.fileno()
        procesoLogin = Process(target=self.servidorLogin, args=(loginSoket,))
        procesoEnter = Process(target=self.enterInput, args=(fn,))
        procesoStatus= Process(target=self.maxStatus)

        procesoEnter.start()
        procesoStatus.start()
        procesoLogin.start()

        while(procesoLogin.is_alive()):
            if(procesoEnter.is_alive() == False or procesoStatus.is_alive() == False):
                break
        
        for tupla in self.conexiones:
            alias = tupla[0]
            conn = tupla[1]
            
            
            dron = crearDron(alias)
            self.drones.append(dron)
            self.mapa[dron.pos] = dron.simbolo
            self.db.insertardron(alias, str(dron.pos), 1, dron.ef, dron.ec, 1, dron.simbolo)

            conn.send(f"(2, 'Tu alias es {alias} y empiezas en la posición ({dron.pos[0]+1},{dron.pos[1]+1})')".encode(FORMAT))
            conn.close()
            
        procesoLogin.terminate()
        procesoEnter.terminate()
        procesoStatus.terminate()

        loginSoket.close()
        

    ## Tarjet de procesoLogin, inicia el servidor de escucha a los drones 
    def servidorLogin(self, loginSoket):

        MAX_CONEXIONES = self.max_players

        while True:
            conn, addr = loginSoket.accept()
            CONEX_ACTIVAS = len(threading.enumerate())-1
            if (CONEX_ACTIVAS <= MAX_CONEXIONES):
                thread = threading.Thread(target=self.logindron, args=(conn, addr))
                thread.start()
                print(f"drones actuales: {CONEX_ACTIVAS}")
                print(f"Faltan {MAX_CONEXIONES-CONEX_ACTIVAS} para empezar la partida")
            else:
                error = "drones máxmos alcanzados"
                print(error)
                msg = (-1, error)
                conn.send(str(msg).encode(FORMAT))
                conn.close()

    ## Handler de login, por cada petición se genera un hilo que será gestionado en esta función.
    def logindron(self, conn, addr):
        confirmacion = f"Conexión aceptada: {addr}"
        print(confirmacion)
        msg = (1, confirmacion)
        conn.send(str(msg).encode(FORMAT))

        print(f"Esperando credenciales de {addr}")
        info = conn.recv(HEADER).decode(FORMAT)
        print(f"Recibido: {info} de {addr}")

        try:
            credenciales = eval(info)
        except:
            print(f"Se nos ha ido {addr}")
            conn.close()
            return
        
        alias = credenciales[0]
        contraseña = credenciales[1]

        dbhilo = NucleoDB()

        for conexion in self.conexiones:
            if alias in conexion:
                print(f"Alias {alias} ya está en la partida")
                msg = (-1, "Este alias ya está en la partida")
                conn.send(str(msg).encode(FORMAT))
                conn.close()
                return

        if dbhilo.loginCredenciales(alias,contraseña):
            print(f"Login correcto de {addr}")
            msg = (1, "Login correcto")
            conn.send(str(msg).encode(FORMAT))
            time.sleep(1)

            conexion = (alias, conn)
            self.conexiones.append(conexion)

            while(True):
                if(len(self.conexiones) == self.max_players):
                    msg = (1, "La partida comenzará dentro de poco")
                    conn.send(str(msg).encode(FORMAT))
                    return
                else:
                    msg = (-1, "Esperando drones...")
                    try:
                        conn.send(str(msg).encode(FORMAT))
                    except:
                        print(f"Se nos ha ido {alias}")
                        conn.close()
                        for i, tupla in enumerate(self.conexiones):
                            if(alias == tupla[0]):
                                self.conexiones.pop(i)
                                break
                        return
                print(f"{alias} esperando...")
                time.sleep(5)
        else:
            print(f"Login incorrecto de {addr}")
            msg = (-1, "Login incorrecto, comprueba alias y contraseña")
            conn.send(str(msg).encode(FORMAT))
            conn.close()
            sys.exit(-1)

    ## Tarjet de procesoEnter
    def enterInput(self,fn):
        sys.stdin = os.fdopen(fn)  #open stdin in this process
        input()

        print("ENTER pulsado")
        return

    ## Tarjet de procesoStatus
    ## Cada 10 segundos, hace una llamada a la base de datos para leer 
    ## la tabla de drones. Si es igual al límite, para el proceso
    def maxStatus(self):

        while(True):
            actuales = len(self.conexiones)
            if(actuales == self.max_players):
                print(f"maxstatus: {actuales}, max players alcanzado, terminando procesos")
                return
            else:
                print(f"maxStatus: {actuales}, me duermo 5 segs")
                time.sleep(5)

    def generarMapa(self):
        mapa = {}
        for i in range(20):
            for j in range(20):

                celda = randint(0,2)

                if(celda == 0):
                    mapa[(i,j)] = " "
                elif(celda == 1):
                    mapa[(i,j)] = "M"
                else:
                    mapa[(i,j)] = "A"
        return mapa

    def dibujarMapa(self):
        nFilas = [x for x in range(4, len(self.drones)+4, 1)]
        nPlayer = 0
        str_mapa = "\n"
        str_mapa += ("     1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19  20      CIUDADES\n")
        str_mapa += ("   ---------------------------------------------------------------------------------\n")
        for i in range(20):
            if(i < 9):
                str_mapa += (f"{i+1}  | ")
            else:
                str_mapa += (Fore.WHITE + f"{i+1} | ")

            for j in range(20):
                val = self.mapa.get((i,j))

                if(val == "M"):
                    color = Fore.RED
                elif(val == "A"):
                    color = Fore.GREEN
                else:
                    color = Fore.YELLOW

                str_mapa+=(color + val)

                if(j == 9):
                    str_mapa += (Fore.BLUE  + " | ")
                else:
                    if('P' in val):
                        str_mapa += (Fore.WHITE + "| ")
                    else:
                        str_mapa += (Fore.WHITE + " | ")

                ## Pintar ciudades
                ## Final de las 2 primeras líneas (i = 0,1 and j = 19)

                if(i == 0):
                    if(j == 19):
                        str_mapa += "    {:<23}{}".format(f"[\u2196 {self.ciudades[0]['ciudad']}, {self.ciudades[0]['temperatura']}ºC]",
                                                          f"[\u2197 {self.ciudades[1]['ciudad']}, {self.ciudades[1]['temperatura']}ºC]")
                if(i == 1):
                    if(j == 19):
                        str_mapa += "    {:<23}{}".format(f"[\u2199 {self.ciudades[2]['ciudad']}, {self.ciudades[2]['temperatura']}ºC]",
                                                          f"[\u2198 {self.ciudades[3]['ciudad']}, {self.ciudades[3]['temperatura']}ºC]")

                ## Pintar drones vivos
                
                ## Final de la línea 4 = dronES (i = 3 and j = 19)
                if(i == 3):
                    if(j == 19):
                        str_mapa += "    dronES"

                ## Final de la línea 5 hasta la línea n donde n son el número de drones ( i = 4...n and j = 19)
                if i in nFilas:
                    dron = self.drones[nPlayer]
                    if(j == 19):
                        if(dron.vivo == 1):
                            estado = "VIVO"
                        else:
                            estado = "MUERTO"
                        str_mapa += "    {} = {:<10}{:<12}{:<14}{:<34}{}".format(dron.simbolo, 
                                                                                 dron.alias, 
                                                                                 f"- nivel {dron.nivel}", 
                                                                                 f"- pos ({dron.pos[0]+1},{dron.pos[1]+1})", 
                                                                                 f"- efectos ({Fore.BLUE+ str(dron.ef)} {Fore.RED+str(dron.ec)}{Fore.WHITE+')'}", 
                                                                                 f"- estado {estado}" )
                        nPlayer += 1

                

            if(i == 9):
                str_mapa += (Fore.BLUE + "\n   ---------------------------------------------------------------------------------\n")
            else:
                str_mapa += ("\n   ---------------------------------------------------------------------------------\n")

        return str_mapa

    def moverdron(self, dron:dron, movimiento):

        # Comprobar que el dron esté vivo
        if(dron.vivo != 1):
            print("Este dron está muerto")
            return
        
        posAntigua = dron.pos 

        # Obtener, a ser posible, la nueva loc (lanza Exception si se sale de los límites del mapa)
        try:
            posNueva = mover(posAntigua, movimiento)
        except Exception as e:
            print(e)
            return

        # Si está dentro del mapa, mirámos qué hay en esa posición
        elemento = self.mapa[posNueva]
        if(elemento == 'A'): # Alimento, nivel++
            dron.nivel += 1
        elif(elemento == 'M'): # Mina, el dron muere
            dron.vivo = 0
            self.mapa[posAntigua] = " "
            self.mapa[posNueva] = " "
            return
        elif(elemento == " "): # Vacio
            pass

        else: # Otro dron o NPC
            for enemigo in self.drones: # Buscamos al enemigo en la posicion
                if(posNueva == enemigo.pos):
                    rival : dron = enemigo 
                    break

            if(dron.nivel > rival.nivel): # Victoria
                rival.vivo = 0
                self.db.modificardron(rival.alias, str(rival.pos), rival.nivel, rival.vivo)
            elif(dron.nivel < rival.nivel): # Derrota
                dron.vivo = 0
                self.mapa[posAntigua] = " "
                return
            else: # Empate
                return

        # Efectos del clima si el dron cambia de zona
        if(cambioZona(posAntigua, posNueva)):
            zona = localizarZonaMapa(posNueva)
            ciudad = self.ciudades[zona]
            
            if(ciudad['temperatura'] <= 10):
                dron.nivel += dron.ef
            elif(ciudad['temperatura'] >= 25):
                dron.nivel += dron.ec

        dron.pos = posNueva
        self.db.modificardron(dron.alias, str(dron.pos), dron.nivel, dron.vivo)
        
        self.mapa[posAntigua] = " "
        self.mapa[posNueva] = dron.simbolo


def main():
    print("Opciones:")
    print("1: Crear juego nuevo")
    print("2: Cargar partida desde último registro de base de datos")
    op = int(input("Selecciona opción: "))
    if(op != 1 and op != 2):
        print("Opción no válida")
        sys.exit()

    engine = Engine(op)
    print("-----------------------------------------------")
    print("Iniciando Kafka")
    print(engine.dibujarMapa())
    engine.iniciarKafka()

main()