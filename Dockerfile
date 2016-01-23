FROM python:3.5

RUN mkdir -p /opt/feasted-api
WORKDIR /opt/feasted-api

COPY ./requirements.txt /opt/feasted-api/requirements.txt
RUN pip install -r /opt/feasted-api/requirements.txt

COPY ./run-server.sh /opt/feasted-api/run-server.sh

COPY ./feasted-api /opt/feasted-api/feasted-api
CMD bash /opt/feasted-api/run-server.sh

