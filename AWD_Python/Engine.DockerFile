FROM alpine
RUN apk add python3
RUN apk add py3-pip
RUN pip install colorama
RUN pip install kafka-python
<<<<<<< HEAD
RUN pip install keyboard
=======
>>>>>>> 0ef1793 (.)
RUN pip install pymongo

ADD Engine /opt/Engine

# sudo docker build -t nucleo -f Nucleo.DockerFile .
# sudo docker run --net mynet --ip 127.0.0.3 -p 3000:3000 -it nucleo bin/sh
