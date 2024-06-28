# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor . La raiz del contenedor
WORKDIR /

# Copiar el script del directorio local al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir flask flask-cors

