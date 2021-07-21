FROM python:latest
COPY client.py /
COPY config.cfg /
COPY master.py /
RUN apt-get update
RUN apt upgrade -y
RUN apt install -y vim
RUN apt install -y iputils-ping