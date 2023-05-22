#!/bin/sh

set -e 
# meme-seeker-db.internal

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST 5432; do
      sleep 1
    done

    echo "PostgreSQL started"
fi
# if [ "$QUEUEENGINE" = "rabbitmq" ]
# then
#     echo "Waiting for rabbitmq..."

#     while ! nc -z rabbitmq 5672; do
#       sleep 1
#     done

#     echo "RabbitMQ started"
# fi

# python db/setup.py && python worker.py

exec "$@"


