#!/bin/bash

# Inicializar ID y puerto
ID=1
PORT=4001

# Ejecutar el comando 8 veces
for i in {1..8}
do
    echo "Ejecutando docker-compose para ID=$ID y puerto $PORT:4000"
    docker-compose run -e ID=$ID -p $PORT:4000 drone
    ((ID++))
    ((PORT++))
done
