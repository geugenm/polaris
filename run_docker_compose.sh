#!/bin/bash

CURRENT_ID="$(id -u):$(id -g)" docker-compose up -d

echo "Waiting for InfluxDB to come up..."
echo "Databases in InfluxDB:"

# This should give us a timeout of roughly 10 seconds.  The curl
# timeout is set to 1 second because the man page warns about less
# accurate timing with smaller timeouts.  If InfluxDB is not ready,
# it's not listening and curl times out quickly.
max_tries=100
i=0

while ! curl \
	-G \
	--max-time 1 \
	http://localhost:8086/query?pretty=true \
	--data-urlencode "q=SHOW DATABASES" 2>/dev/null ; do
    sleep 0.1
    i=$((i + 1))
    if [[ $i -gt $max_tries ]] ; then
	echo "InfluxDB container is not coming up. Is something wrong?"
	exit 1
    fi
done

cat <<EOF

To create a new database:

	curl -XPOST http://localhost:8086/query --data-urlencode 'q=CREATE DATABASE new_database'

Grafana can be reached here: http://127.0.0.1:3000
Username: admin
Password: password
EOF
