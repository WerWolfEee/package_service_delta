FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY . /code

RUN apt update && \
    apt install -y --assume-yes python3-dev && \
    pip3 install -r requirements.txt
