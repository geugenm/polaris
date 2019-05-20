#!/bin/bash

CURRENT_ID="$(id -u):$(id -g)" docker-compose up -d

echo "Waiting for InfluxDB to come up..."
sleep 2
echo "Databases in InfluxDB:"

curl -G \
     http://localhost:8086/query?pretty=true \
     --data-urlencode "q=SHOW DATABASES"

echo
echo "To create a new database:"
echo "curl -XPOST http://localhost:8086/query --data-urlencode 'q=CREATE DATABASE new_database'"

echo "Grafana can be reached here: http://127.0.0.1:3000"
echo "Username: admin"
echo "Password: password"
