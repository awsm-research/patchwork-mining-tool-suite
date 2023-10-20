FROM badouralix/python-scrapy:latest

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# COPY ./requirements.txt /tmp/requirements.txt
COPY . /scrapy_docker_app
WORKDIR /scrapy_docker_app
EXPOSE 6800

RUN pip install --upgrade pip && \
    # apk add gcc libc-dev libffi-dev && \
    pip install -r /scrapy_docker_app/requirements.txt && \
    rm -rf /scrapy_docker_app/requirements.txt && \
    adduser \
        --disabled-password \
        --no-create-home \
        scrapy-user

USER scrapy-user