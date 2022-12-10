#!/usr/bin/env bash

echo "Waiting for Tika to launch on $TIKA_PORT..."
while ! nc -z $TIKA_HOST $TIKA_PORT; do
  sleep 1
done
echo "Tika launched"

echo "Waiting for PostgreSQL to launch on $POSTGRES_PORT..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
echo "PostgreSQL launched"

echo "Waiting for ElasticSearch to launch on $ELASTICSEARCH_PORT..."
while ! nc -z $ELASTICSEARCH_HOST $ELASTICSEARCH_PORT; do
  sleep 1
done
echo "ElasticSearch launched"

echo "Waiting for Redis to launch on $REDIS_PORT..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done
echo "Redis launched"


echo "Launching the server"
uvicorn app:app --host 0.0.0.0 --port 9100
