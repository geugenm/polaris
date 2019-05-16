# Polaris

The goal of this project is to analyze data from the [SatNOGS Network](https://network.satnogs.org/).

## Cloning

To clone this repo for the first time, run:

```
git clone --recurse-submodules https://gitlab.com/crespum/polaris.git
```

## Installation of dependencies

For developers:
```bash
pip install -r requirements-dev.txt
```

For users:
```bash
pip install -r requirements.txt
```

## Running notebooks

Run in the top level of this repo:

```bash
jupyter notebook
```

## What it does

 * Parse data from SatNOGS using Kaitai struct
 * Analyze dependencies in satellite telemetry

## InfluxDB and Grafana

InfluxDB and Grafana have been configured to run with
`docker-compose`.  (At the moment these are not configured to do much,
but they will be useful for future development.)

For more details, see `InfluxDB.md`.
