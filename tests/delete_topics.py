from json import dumps
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import time
import random
import logging


def delete_topic():
    a = AdminClient({"bootstrap.servers": "localhost:19092"})

    topics = ["telemetry"]
    fs = a.delete_topics(topics, operation_timeout=30)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} deleted".format(topic))
        except Exception as e:
            print("Failed to delete topic {}: {}".format(topic, e))


if __name__ == "__main__":
    delete_topic()