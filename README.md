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
git clone --recurse-submodules https://gitlab.com/crespum/polaris.git

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install project dependencies
pip install -r requirements.txt

# (devs) Install dependencies for development
pip install -r requirements-dev.txt

# Change directory to utils/satnogs-decoders
cd utils/satnogs-decoders/

# Run docker-ksc script to compile KSY to Python code (Requires Docker)
# The following command will output the compiled files under satnogsdecoders/decoder directory.
./contrib/docker-ksc.sh

# Install the package from source code directory using following command
pip install -e .

# Change directory to utils/glouton-satnogs-data-downloader
cd ../../utils/glouton-satnogs-data-downloader

# Install dependencies
pip install -r requirements.txt
```

## Running the code
```
# Go to the polaris directory within this repo
cd polaris
$ python3 polaris.py -h
usage: polaris [-h] {data_fetch,learning,data_viz} ...

Tool for analyzing satellite telemetry

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  valid subcommands

  {data_fetch,learning,data_viz}
    data_fetch          data-fetch help
    learning            learning help
    data_viz            data-viz help

# To fetch and decode the data from the SatNOGS network, use the following command
$ python3 polaris.py data_fetch

```

### More info for developers

Building the package
```bash
python setup.py bdist_wheel
```

Format the code before commiting, otherwise the CI engine will fail:
```bash
# Auto-format the code
tox -e yapf-apply -e isort-apply

# Verify CI test passes
tox
```

## InfluxDB and Grafana

InfluxDB and Grafana have been configured to run with `docker-compose`. (At the moment these are not configured to do much, but they will be useful for future development.)

For more details, see [docs/InfluxDB.md](docs/InfluxDB.md).
