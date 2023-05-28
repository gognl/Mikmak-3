FROM ubuntu:20.04
WORKDIR /app/central_server_files
ENV PYTHONPATH "${PYTHONPATH}:/app/"
COPY requirements.txt requirements.txt

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install python3.9 python3-pip -y

RUN apt install python3.9-dev -y
RUN apt install mysql-client -y
RUN apt install libmysqlclient-dev -y
RUN apt install libssl-dev -y

RUN python3.9 -m pip install -r requirements.txt

COPY . .