FROM python:3.5

RUN mkdir -p /opt/feasted_api
WORKDIR /opt/feasted_api

COPY ./requirements.txt /opt/feasted_api/requirements.txt
RUN pip install -r /opt/feasted_api/requirements.txt

COPY ./run-server.sh /opt/feasted_api/run_server.sh

COPY ./feasted_api /opt/feasted_api/feasted_api
CMD bash /opt/feasted_api/run-server.sh

