#!/bin/bash

# A Small but Useful(tm) script to start our docker-compose
# environment, make sure that the permissions of the volume inside the
# containers match those of the user running it, and say when InfluxDB
# and Grafana are ready to go.

CURRENT_ID="$(id -u):$(id -g)" docker-compose up -d

# This should give us a timeout of roughly 30 seconds; in testing on
# my laptop, Grafana took up to 23 seconds to come up.
MAX_TRIES=300

wait_for() {
    TARGET=$1
    # The curl timeout is set to 1 second because the man page warns
    # about less accurate timing with smaller timeouts.  If there's
    # nothing listening, curl times out quickly.
    CURL="curl --silent --max-time 1"
    i=0
    case $TARGET in
	influxdb)
	    URL="http://localhost:8086/query?pretty=true&q=SHOW%20DATABASES"
	    ;;
	grafana)
	    URL="http://127.0.0.1:3000"
	    # We're not interested in the Grafana output
	    CURL_OPTS="--output /dev/null"
	    ;;
	*)
	    echo "Don't know how to wait for $TARGET !"
	    return 3
	    ;;
    esac
    echo "Waiting for $TARGET..."
    while ! $CURL $CURL_OPTS $URL ; do
	sleep 0.1
	i=$((i + 1))
	if [[ $i -gt $MAX_TRIES ]] ; then
	    echo "$TARGET container is not coming up. Is something wrong?"
	    return 1
	fi
    done
    i=$((i / 10))
    echo "$TARGET came up in $i seconds."
}

wait_for influxdb
wait_for grafana

cat <<EOF

To create a new database:

	curl -XPOST http://localhost:8086/query --data-urlencode 'q=CREATE DATABASE new_database'

Grafana can be reached here: http://127.0.0.1:3000
Username: admin
Password: password
EOF
