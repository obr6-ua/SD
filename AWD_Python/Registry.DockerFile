FROM alpine
ENV entorno=1
RUN apk add python3
RUN apk add py3-pip
RUN pip install colorama

ADD Registry /opt/Registry

# sudo docker build -t nucleo -f Nucleo.DockerFile .
# sudo docker run --net mynet --ip 127.0.0.3 -p 3000:3000 -it nucleo bin/sh
