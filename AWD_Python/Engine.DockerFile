
# Utilizar una imagen base de Alpine
FROM alpine:latest

# Instalar Python y Pip
RUN apk add --no-cache python3 py3-pip

# Si es necesario, instalar dependencias para la compilación de paquetes de Python
# RUN apk add --no-cache python3-dev build-base

# Crear un entorno virtual (opcional en Alpine, pero puede ser una buena práctica)
RUN python3 -m venv /app/venv

# Establecer el directorio de trabajo
WORKDIR /app

# Asegurarse de que se usa pip del entorno virtual
ENV PATH="/app/venv/bin:$PATH"

# Instalar paquetes en el entorno virtual
# Aquí, usamos directamente el pip del entorno virtual
RUN pip install kafka-python pymongo colorama prettytable

ADD Engine /opt/Engine

# sudo docker build -t nucleo -f Nucleo.DockerFile .
# sudo docker run --net mynet --ip 127.0.0.3 -p 3000:3000 -it nucleo bin/sh
