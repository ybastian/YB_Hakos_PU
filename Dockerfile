# syntax=docker/dockerfile:1
FROM python:3.14-alpine

RUN apk update \
    && apk upgrade \
    && apk add build-base libpq libpq-dev

ENV FLASK_APP=prod.py

WORKDIR /vds

COPY requirements-prod.txt ./requirements.txt
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY webapp webapp/
COPY migrations migrations/
COPY prod.py ./
COPY app.py ./
COPY docker-startup.sh ./

EXPOSE 5000/tcp
ENTRYPOINT [ "/bin/sh", "-c" ]
CMD [ "./docker-startup.sh" ]
