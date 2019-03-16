# Polaris

Python3 tool to analyze a satellite set of telemetry to understand links/dependencies among different subsystems. The telemetry is currently retrieved from the [SatNOGS Network](https://network.satnogs.org/).

## Project structure

```
polaris/               - Project source code
    data_fetch/        - Module to fetch and prepare data for the analysis
    data_viz/          - Module to visualize the analysis results
    learn/             - Module to perform the data analysis
    polaris.py         - Polaris entry point

playground/            - Exploratory tests
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
```

## Running the code
```
$ python polaris.py -h
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

```

### More info for developers

Building the package
```bash
python setup.py bdist_wheel
```

If you want to **know more**, join our [Matrix room](https://riot.im/app/#/room/#polaris:matrix.org)
