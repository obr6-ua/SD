from kafka import KafkaConsumer, KafkaProducer
from multiprocessing import Process

import sys
import socket
import os
import random

from colorama import Fore, Back, Style

FORMAT = 'utf-8'
HEADER = 128
POSSIBLE_MOVES = ['w', 'a', 's', 'd', 'aw', 'wa', 'wd', 'dw', 'sd', 'ds', 'as', 'sa']

def pedirMovimiento():
    rand = random.choice(POSSIBLE_MOVES)
    mov = rand
    return mov

def consumirMapa():

    mapConsumer = KafkaConsumer('map',bootstrap_servers=SERVER_KAFKA)
    
    for mapa in mapConsumer:
        msg = mapa.value.decode(FORMAT)

        if('FIN DE PARTIDA' in msg):
            print('\n')
            print(msg)
            return
        else:
            print(msg)


def producirMov(id_npc, fn):
    movProducer = KafkaProducer(bootstrap_servers=SERVER_KAFKA)
    sys.stdin = os.fdopen(fn)  #open stdin in this process

    while(True):
        mov = pedirMovimiento()
        movProducer.send('moves', f"('{id_npc}', '{mov}')".encode(FORMAT))
        movProducer.flush()

def iniciarKafka(id_npc):

    fn = sys.stdin.fileno()
    procesoConsumer = Process(target=consumirMapa)
    procesoProducer = Process(target=producirMov, args=(id_npc,fn))

    procesoConsumer.start()
    procesoProducer.start()

    while(procesoConsumer.is_alive()):
        if(procesoProducer.is_alive() == False):
            break

    procesoConsumer.terminate()
    procesoProducer.terminate()

    sys.exit(0)


def logearse(host, port):

    ADDR_log = (host, port) 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR_log)
    except:
        print("El servidor está desconectado o ya hay una partida en curso")
        client.close()
        return

    print (f"Establecida conexión en [{ADDR_log}]")

    ## Confirmación conexión
    recibido = client.recv(HEADER).decode(FORMAT)
    msg = eval(recibido)

    client.close()
        
# ip y puerto del broker
def main(): 
    global SERVER_KAFKA

    SERVER_KAFKA = sys.argv[1].split(":")[0]
    logearse(sys.argv[1].split(":")[0], int(sys.argv[1].split(":")[1]))


if __name__ == "__main__":
    main()

