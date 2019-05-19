# InfluxDB and Grafana

One of the goals of Polaris is to visualize the predictions made, and
anomalies detected, by the software.  To help with that, a local
development environment can be run with `docker-compose`.  (This is
also the stack that the SatNOGS project uses to power
[dashboard.satnogs.org](https://dashboard.satnogs.org)).

Currently, InfluxDB and Grafana are not configured to do much.  This
will change.

# State

InfluxDB and Grafana will save files at `docker/influxdb/data` and
`docker/grafana/data`, respectively.  Any database created, data
added, or Grafana dashboards should persist and be available the next
time the environment is started.

To clean those files, see [Cleaning](#cleaning).

# Configuration

InfluxDB and Grafana are configured by application-specific
environment variables; these are stored at
`docker/influxdb/env.influxdb` and `docker/grafana/env.grafana`,
respectively.  Information on what those settings do can be found
here:

- [InfluxDB](https://hub.docker.com/_/influxdb/)
- [Grafana](https://grafana.com/docs/installation/docker/)

# Starting

```
make docker-compose-start
```

# Accessing

The InfluxDB HTTP API can be reached at http://localhost:8086.  No
authentication is required.  (**NOTE:** This will *not* be the case in
production!)

An empty database is created at startup named `polaris`.

An InfluxDB shell can be launched like so:

```
make influxdb-shell
```

Grafana can be reached at http://127.0.0.1:3000.  The username and
password are both "admin" (no quotes).

# Stopping

```
make docker-compose-stop
```

# Cleaning

This will remove all data files for InfluxDB and Grafana.  It's great
for a clean start...but you will not get your data back.

```
make docker-compose-clean
```
