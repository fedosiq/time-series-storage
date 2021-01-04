from time import sleep
from json import dumps
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import time
import random
import logging


def create_topic(num_partitions=3):
    a = AdminClient({"bootstrap.servers": "localhost:19092"})

    telemetry = [NewTopic("telemetry", num_partitions=num_partitions, replication_factor=1)]

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


if __name__ == '__main__':
    create_topic()
    start_producer()
