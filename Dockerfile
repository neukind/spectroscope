FROM python:3.8-buster

COPY . /opt/ethmonitor

WORKDIR /opt/ethmonitor
RUN pip install -r requirements.txt
RUN ./build_proto_libs.sh