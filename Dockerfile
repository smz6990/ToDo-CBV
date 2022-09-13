FROM python:3.9.6-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY ./core /app/

RUN mkdir -p /app/staticfiles
RUN python manage.py collectstatic --no-input