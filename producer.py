from time import sleep
from json import dumps
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import time
import random


def create_topic(n_partitions=3):
    # a = AdminClient({"bootstrap.servers": "localhost:19092,localhost:29092"})
    a = AdminClient({"bootstrap.servers": "localhost:19092"})

    telemetry = [NewTopic("telemetry", num_partitions=n_partitions, replication_factor=1)]

    fs = a.create_topics(telemetry)

    for topic, f in fs.items():
        try:
            f.result()
            print(f"Topic {topic} created")
        except Exception as e:
            print(f"Failed to create topic {topic}: {e}")


def start_producer():
    producer = Producer({
        "bootstrap.servers": "localhost:19092",
        "enable.idempotence": True,
        "request.required.acks": "all",
    })
    for e in range(1000):
        timenow = int(time.time())
        data = {
            "id": random.choice(range(1000)),
            "timestamp": timenow,
            "data": e
        }
        producer.produce(topic='telemetry', value=dumps(data))
        print(f"{data} sent")
        sleep(1)


def start_batching_producer(batch_size=2):
    producer = Producer({
        "bootstrap.servers": "localhost:19092",
        "enable.idempotence": True,
        "request.required.acks": "all",
    })
    for e in range(1000):
        timenow = int(time.time())
        make_row = lambda: {
            "id": random.choice(range(1000)),
            "timestamp": timenow,
            "data": e
        }
        data = "\n".join([dumps(make_row()) for _ in range(batch_size)])
        producer.produce(topic='telemetry', value=data)
        print(f"{data} sent")
        sleep(1)


if __name__ == '__main__':
    # create_topic()
    start_batching_producer(1000)
