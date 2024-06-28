# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /opt/Engine

# Copiar el script del directorio local al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir requests pymongo cryptography kafka-python prettytable flask flask-cors

