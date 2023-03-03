#!/bin/sh

set -e 

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z db 5432; do
      sleep 1
    done

    echo "PostgreSQL started"
fi
if [ "$QUEUEENGINE" = "rabbitmq" ]
then
    echo "Waiting for rabbitmq..."

    while ! nc -z rabbitmq 5672; do
      sleep 1
    done

    echo "RabbitMQ started"
fi

exec "$@"


