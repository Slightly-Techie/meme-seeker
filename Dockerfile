FROM python:3.8-alpine
LABEL maintainer="Tonny-Bright Sogli"

ENV PYTHONUNBUFFERED 1

ENV DATABASE postgres
ENV QUEUEENGINE rabbitmq

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
COPY ./scripts /scripts
WORKDIR /app

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    meme-user && \
    chmod -R +x /scripts && \
    touch /var/log/output.log && \
    chown -R meme-user:meme-user /var/log/output.log && \
    chmod 755 -R /var/log/output.log
    

ENV PATH="/scripts:/py/bin:$PATH"

USER meme-user

ENTRYPOINT [ "run.sh" ]
