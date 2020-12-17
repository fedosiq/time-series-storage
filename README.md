# ClickHouse - Kafka

## Deploy

Download and start all docker images.

```
$ docker-compose up
```

Connect to ClickHouse using https://tabix.io/:
- Username: default
- Host: https://localhost:8123
- Name: <choose any>
  
Connect to Kafka using Web UI on http://localhost:8000;

Connect to Grafana on localhost:3000 as admin (pass: admin) and add Prometheus data source (http://prometheus:9090);

Add kafka dashboard:
Create -> import -> import via grafana.com -> enter dashboard id (721)


Finally, start a producer:

```sh
$ pip install -r requirements.txt
$ python producer.py
```

## Roadmap

### Initial implementation

- Picture with a project architecture;

- ~~Add ClickHouse to docker-compose~~;
- ~~Add Kafka to docker-compose~~;
- ~~Write a simple artificial producer~~;

- <details><summary><strike>Sharding/Replication for Kafka</strike></summary>

  Sharding is implemented by partitioning Kafka topics and is specified by `partitions` parameter. Replication is specified by `replication factor` - how many   replicas should be distributed across available nodes. 

  Links:
  - How replication works in Kafka: https://kafka.apache.org/documentation/#replication
  </details>

- Sharding/Replication for ClichHouse;
- <details><summary><strike>Kafka: producer -> Kafka "exact-once" reliable delivery</strike></summary>

  The reliability/durability is ensured by KafkaProducer `acks` parameter, which specify the number of required acknowledgemets from Kafka nodes. See: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html#kafka.KafkaProducer

  > The number of acknowledgments the producer requires the leader to have received before considering a request complete. This controls the durability of records that are sent. ...

  The "exact-once" delivery sematics supported by "idempotence" parameter, which force Kafka to make deduplication of messages. Links: 
  - https://kafka.apache.org/documentation/#semantics (Since 0.11.0.0, the Kafka producer also supports an idempotent delivery option which guarantees that resending will not result in duplicate entries in the log);
  - https://www.cloudkarafka.com/blog/2019-04-10-apache-kafka-idempotent-producer-avoiding-message-duplication.html

  </details>

- Kafka/ClickHouse: Kafka -> Consumer "exact-once" delivery or some deduplication mechanism (add a comment);
- ClickHouse: research and prevent data losses;
- Make a simple notes with a list of circumstances by which our system may fail;

### Performance testing
- ~~Add metrics storage (Prometheus or Graphite). Kafka and CH both should support it~~;
- ~~Connect ClickHouse with metrics storage~~;
- ~~Connect Kafka with metrics storage~~;
- Write a device test load using python + locust or python + multiprocessing or smth else;
- Make stress test;
- May be deploy all of it on the Google Cloud or AWS (with free subscription);
- Make perfomance tests depending on number of nodes available;
- Make some test on fault-tolerance (Does our system works properly when some nodes unavailable?);

