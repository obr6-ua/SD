#!/bin/bash

# Inicializar ID y puerto
ID=1
PORT=4001

# Ejecutar el comando 8 veces en terminales separadas
for i in {1..8}
do
    # Comando a ejecutar en la nueva terminal
    COMMAND="echo 'Ejecutando docker-compose para ID=$ID y puerto $PORT:4000'; docker-compose run -e ID=$ID -p $PORT:4000 drone"

    # Abrir una nueva terminal y ejecutar el comando
    gnome-terminal -- /bin/bash -c "$COMMAND"
    
    # Incrementar ID y PORT
    ((ID++))
    ((PORT++))
done
