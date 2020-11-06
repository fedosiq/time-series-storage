from time import sleep
from json import dumps
from kafka import KafkaProducer
import time
import random

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda x: dumps(x).encode('utf-8'))

for e in range(1000):
    timenow = int(time.time())
    data = {
        "id": random.choice(range(1000)),
        "timestamp": timenow,
        "data": e
    }
    producer.send('test', value=data)
    sleep(1)
