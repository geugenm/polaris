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
$ pip3 install polaris-ml
```

We recommend to install it inside a Python virtual environment:
```bash
# Create the virtual env
$ python3 -m venv .venv

# Activate it
$ source .venv/bin/activate

# Install Polaris from Pypi
$ (.venv) pip install polaris-ml
```

## Running the code

```bash
$ (.venv) polaris --help
Usage: polaris [OPTIONS] COMMAND [ARGS]...

  Tool for analyzing satellite telemetry

Options:
  --version   Show the version and exit.
  --help      Show this message and exit.

Commands:
  fetch       Download data set(s)
  learn       Analyze data
  viz         Display results


# To fetch and decode data from the SatNOGS network, run:
$ (.venv) polaris fetch -s 2019-08-10 -e 2019-10-5 LightSail-2 /tmp/
# Note: this may take some time.

# Data will be saved at /tmp/normalized_frames.json
$ (.venv) head /tmp/normalized_frames.json
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
$ (.venv) polaris learn -g /tmp/new_graph.json /tmp/normalized_frames.json
# Note: depending on your hardware, this may take some time.

# To see a visualization of these results, run:
$ (.venv) polaris viz /tmp/new_graph.json
# Then visit http://localhost:8080 in your browser
```
## MLflow

Installing Polaris will install MLflow as a dependency. At this time Polaris is using MLflow during the cross check dependencies process and the database is stored in the current working directory under the mlruns folder.

To view the logs into MLflow, you have to run that command line from where the mlruns folder is located : 
```bash
$ mlflow ui
```
This command will start the tracking ui server at http://localhost:5000.

## More info for developers

Building the package from the sources:
```bash
# Clone the repo
$ git clone https://gitlab.com/crespum/polaris.git

# Activate the virtual environment:
$ source .venv/bin/activate

# Build and install the package in editable mode; any changes
# to your code will be reflected when you run polaris.
$ (.venv) pip install -e .
```

It is important to format the code before commiting, otherwise the
CI engine will fail. We have a tox command setup to run tests before
committing so you will never have to push failing pipelines. Code
linting is also done to ensure the code does not have any errors
before committing.

First you will have to install Prettier. Be sure to have a node version equal or greater than version 10.13.0 :

```bash
$ npm install -g prettier
```
You can learn more about npm [here](https://www.npmjs.com/).

```bash
# Install tox to execute CI tasks
$ (.venv) pip install tox

# Auto-format the code
$ (.venv) tox -e yapf-apply -e isort-apply -e prettier-apply
______________________ summary______________________
  yapf-apply: commands succeeded
  isort: commands succeeded
  prettier-apply: commands succeeded
  congratulations :)

# Verify CI test passes
$ (.venv) tox
# If all goes well, you will get something like this:
______________________ summary______________________
  flake8: commands succeeded
  isort: commands succeeded
  yapf: commands succeeded
  pylint: commands succeeded
  build: commands succeeded
  pytest: commands succeeded
  prettier: commands succeeded
  congratulations :)

```
You can learn more about tox [here](https://tox.readthedocs.io/en/latest/).
