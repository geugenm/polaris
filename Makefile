docker-compose-start:
	./run_docker_compose.sh

docker-compose-stop:
	docker-compose stop

docker-compose-clean:
	rm -rf docker/influxdb/data/*
	rm -rf docker/grafana/data/*

influxdb-shell:
	docker exec -it influxdb influx
