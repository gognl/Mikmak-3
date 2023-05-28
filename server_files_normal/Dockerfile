FROM ubuntu:20.04
WORKDIR /app/server_files_normal
ENV PYTHONPATH "${PYTHONPATH}:/app/"
COPY requirements.txt requirements.txt

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install python3.9 python3-pip -y

RUN python3.9 -m pip install -r requirements.txt

COPY . .