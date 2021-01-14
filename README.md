# ClickHouse - Kafka

## Requirements

- docker-compose (tested with 1.27.4, build 40524192)
- docker (tested with 20.10.2, build 2291f61)
- python 3.7+

## Run

Build and run all services.

```sh
$ docker-compose build
$ docker-compose up
```

After all services are ready, go to `tests`, install all required dependencies and create `telemetry` topic:

```sh
$ cd tests
$ pip3 install -r requirements.txt
$ python3 create_topics.py
```

After topic is created, you can start to load the deployed services with low-freq messages (default 1 Hz):

```sh
$ cd tests
$ python3 producer.py
```

## Monitoring/Observation

### ClickHouse

Connect to ClickHouse using https://tabix.io/:
- Username: default
- Host: https://localhost:8123 (You can any other available port, see `docker-compose.yaml`)
- Name: <choose any>

### Kafka

You can access Kafka topics UI on http://localhost:8000;

### Grafana

Connect to Grafana on http://localhost:3000
- Username: admin
- Password: admin

After login, you need to specify:
- Data source. Choose Prometheus and enter `http://prometheus:9090` in URL field.
- Import a custom dashboard. See `grafana` dir. 
