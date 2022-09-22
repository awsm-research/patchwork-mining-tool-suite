FROM python:3.9-alpine3.13

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./django_docker_app /home/code_review_mining/django_docker_app
COPY ./scrapy_docker_app /home/code_review_mining/scrapy_docker_app
# WORKDIR /django_docker_app
WORKDIR /home/code_review_mining
EXPOSE 8000

RUN pip install --upgrade pip && \
    apk add gcc libc-dev libffi-dev && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

USER django-user