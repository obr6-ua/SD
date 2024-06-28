# Usa una imagen base de Node.js
FROM node:14

# Crea el directorio de la aplicación
WORKDIR /app

# Copia el contenido de la carpeta awd_python al contenedor
COPY ./awd_python /app

# Instala las dependencias de la aplicación
RUN npm install

# Expone el puerto de desarrollo de Vue.js
EXPOSE 8080
EXPOSE 8081

# Comando para correr la aplicación
CMD ["sh", "-c", "npm run serve"]
