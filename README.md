# Polaris

[![pipeline status](https://gitlab.com/crespum/polaris/badges/master/pipeline.svg)](https://gitlab.com/crespum/polaris/commits/master)
[![coverage report](https://gitlab.com/crespum/polaris/badges/master/coverage.svg)](https://gitlab.com/crespum/polaris/commits/master)

Python3 tool to analyze a satellite set of telemetry to understand links/dependencies among different subsystems. The telemetry is currently retrieved from the [SatNOGS Network](https://network.satnogs.org/).

If you want to **know more**:

- join our [Matrix room](https://riot.im/app/#/room/#polaris:matrix.org)

- read the [project wiki](https://gitlab.com/crespum/polaris/wikis/Home)

- read the blog post [Analyzing Lightsail-2 Telemetry with Polaris](https://blog.crespum.eu/analyzing-lightsail-2-telemetry-with-polaris/)

## Project structure

```
contrib/               - code that is not directly dependent on Polaris, but is used in the project
docs/                  - Some documentation on the project (though more is in the wiki)
docker/                - Docker files for Grafana and InfluxDB
polaris/               - Project source code
    fetch/             - Module to fetch and prepare data for the analysis
    viz/               - Module to visualize the analysis results
    learn/             - Module to perform the data analysis
    polaris.py         - Polaris entry point

tests/                 - Project unit tests
playground/            - Exploratory tests
```

## Installation

```bash
# Clone the repo
$ git clone https://gitlab.com/crespum/polaris.git

# Run `make setup` -- this will:
# - Create virtual environment
# - Install project dependencies
# - Run docker-ksc script to compile KSY to Python code (requires Docker)
# - Install polaris into your virtual environment
$ make setup

# To use the virtual environment:
$ source .venv/bin/activate
```

You can also use the deployed PyPI package using:

```bash
$ pip install polaris-ml
```

## Running the code
```bash
# Activate the virtual environment:
$ source .venv/bin/activate

# Go to the bin directory within this repo and run the command
$ cd bin
$ python3 polaris -h
Tool for analyzing satellite telemetry

Options:
  --help  Show this message and exit.

Commands:
  fetch     Download data set(s)
  learn     Analyze data
  viz       Displaying results

# To fetch and decode data from the SatNOGS network, run:
$ polaris fetch -s 2019-08-10 -e 2019-10-5 LightSail-2 /tmp/
# Note: this may take some time.

# Data will be saved at /tmp/normalized_frames.json
$ head /tmp/normalized_frames.json
[
    {
        "time": "2019-09-12 08:14:42",
        "measurement": "",
        "tags": {
            "satellite": "",
            "decoder": "Lightsail2",
            "station": "",
            "observer": "",
            "source": "",
[...]


# To learn from that data, run:
$ polaris learn -g /tmp/new_graph.json /tmp/normalized_frames.json
# Note: depending on your hardware, this may take some time.

# To see a visualization of these results, run:
$ polaris viz /tmp/new_graph.json
# Then visit http://localhost:8080 in your browser
```

### More info for developers

Building the package
```bash
# Activate the virtual environment:
$ source .venv/bin/activate

# Build and install the package in editable mode; any changes
# to your code will be reflected when you run polaris.
$ pip install -e .
```

Format the code before commiting, otherwise the CI engine will fail:
```bash
# Auto-format the code
$ tox -e yapf-apply -e isort-apply

# Verify CI test passes
$ tox
```

## InfluxDB and Grafana

InfluxDB and Grafana have been configured to run with `docker-compose`. (At the moment these are not configured to do much, but they will be useful for future development.)

For more details, see [docs/InfluxDB.md](docs/InfluxDB.md).
