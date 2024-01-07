#!/bin/bash

# Inicializar ID y puerto
ID=1
PORT=4001
API=N  # Valor inicial de API

# Ejecutar el comando 8 veces
for i in {1..8}
do
    # Cambiar API a S después de las primeras 4 iteraciones
    if [ $i -eq 5 ]; then
        API=S
    fi

    echo "Ejecutando docker-compose para ID=$ID, puerto $PORT:4000 y API=$API"
    docker-compose run -e ID=$ID -e API=$API -p $PORT:4000 drone
    ((ID++))
    ((PORT++))
done
