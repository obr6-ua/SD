FROM alpine

# Definir la variable de entorno
ENV entorno=1

# Instalar python3 y pip
RUN apk add --no-cache python3 py3-pip

# Crear un entorno virtual para Python
RUN python3 -m venv /opt/venv

# Asegurar que se use el pip del entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Instalar pymongo dentro del entorno virtual
RUN pip install pymongo

# Agregar los archivos de tu aplicación
ADD Registry .

# Comandos para construir y ejecutar el contenedor
# sudo docker build -t nucleo -f Nucleo.DockerFile .
# sudo docker run --net mynet --ip 127.0.0.3 -p 3000:3000 -it nucleo bin/sh
