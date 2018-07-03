FROM python:3-alpine3.7

COPY . /srv/app
WORKDIR /srv/app

RUN pip install -r requirements.txt
