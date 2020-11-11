from time import sleep
from json import dumps
from confluent_kafka import Producer
import time
import random
import logging


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
    print("data sent")
    sleep(1)
