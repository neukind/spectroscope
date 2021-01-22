FROM python:3.9-buster

COPY . /opt/spectroscope
WORKDIR /opt/spectroscope

RUN pip install .[alerta,webhook,zenduty]

ENTRYPOINT ["spectroscope"]
