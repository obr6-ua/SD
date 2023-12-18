FROM alpine

# Instalar python3 y pip
RUN apk add --no-cache python3 py3-pip

# Crear un entorno virtual
RUN python3 -m venv /opt/venv

# Asegurar que usamos el pip del entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Instalar paquetes
RUN pip install kafka-python pymongo prettytable requests cryptography

# Agregar los archivos de tu aplicación
ADD Drone .
