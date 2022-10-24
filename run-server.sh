#!/usr/bin/env bash

echo "Waiting for Tika to launch on $TIKA_PORT..."
while ! nc -z $TIKA_HOST $TIKA_PORT; do
  sleep 1
done
echo "Tika launched"

echo "Waiting for PostgreSQL to launch on $POSTGRESQL_PORT..."
while ! nc -z $POSTGRESQL_HOST $POSTGRESQL_PORT; do
  sleep 1
done
echo "PostgreSQL launched"

echo "Waiting for ElasticSearch to launch on $ELASTICSEARCH_PORT..."
while ! nc -z $ELASTICSEARCH_HOST $ELASTICSEARCH_PORT; do
  sleep 1
done
echo "ElasticSearch launched"


echo "Launching the server"
streamlit run web/site.py --server.address='0.0.0.0' --server.port=9100 --theme.base='dark'
