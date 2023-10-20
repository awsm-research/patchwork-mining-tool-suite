FROM python:3.9-alpine3.13

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# COPY ./requirements.txt /tmp/requirements.txt
COPY . /django_docker_app
WORKDIR /django_docker_app
EXPOSE 8000

RUN python3 -m pip install -r /django_docker_app/requirements.txt && \
    rm -rf /django_docker_app/requirements.txt && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

USER django-user