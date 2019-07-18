# Polaris

[![pipeline status](https://gitlab.com/crespum/polaris/badges/master/pipeline.svg)](https://gitlab.com/crespum/polaris/commits/master)
[![coverage report](https://gitlab.com/crespum/polaris/badges/master/coverage.svg)](https://gitlab.com/crespum/polaris/commits/master)

Python3 tool to analyze a satellite set of telemetry to understand links/dependencies among different subsystems. The telemetry is currently retrieved from the [SatNOGS Network](https://network.satnogs.org/).

If you want to **know more**, join our [Matrix room](https://riot.im/app/#/room/#polaris:matrix.org)

## Project structure

```
polaris/               - Project source code
    data_fetch/        - Module to fetch and prepare data for the analysis
    data_viz/          - Module to visualize the analysis results
    learning/          - Module to perform the data analysis
    polaris.py         - Polaris entry point

tests/                 - Project unit tests
playground/            - Exploratory tests
utils/                 - Dependencies that are submodules for this repo
```

## Installation

```bash
# Clone the repo
$ git clone --recurse-submodules https://gitlab.com/crespum/polaris.git

# Run `make setup` -- this will:
# - Create virtual environment
# - Install project dependencies
# - Run docker-ksc script to compile KSY to Python code (requires Docker)
# - Install polaris into your virtual environment
$ make setup

# To use the virtual environment:
$ source .venv/bin/activate
```

## Running the code
```
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
  learning  learning help
  viz       data-viz help

# To fetch and decode the data from the SatNOGS network, use the following command
$ python bin/polaris fetch -s 2019-06-01 -e 2019-06-07 2019-elfin-a
```

### More info for developers

Building the package
```bash
# Activate the virtual environment:
$ source .venv/bin/activate

# Build and install the package
$ python setup.py install
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
