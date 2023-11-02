FROM alpine
RUN apk add python3

ADD Clima /opt/Clima

# sudo docker build -t clima -f Clima.DockerFile .
# sudo docker run --net mynet --ip 127.0.0.2 -it clima bin/sh

