docker-compose-start:
	./run_docker_compose.sh

docker-compose-stop:
	docker-compose stop

docker-compose-clean:
	rm -rf docker/influxdb/data/*
	rm -rf docker/grafana/data/*

influxdb-shell:
	docker exec -it influxdb influx

setup:
	( \
		python3 -m venv .venv ; \
		source .venv/bin/activate ; \
		pip install -r requirements-dev.txt ; \
		cd utils/satnogs-decoders ; \
		./contrib/docker-ksc.sh ; \
		pip install -e . ; \
		cd ../.. ; \
		python3 setup.py install ; \
	)
