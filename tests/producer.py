import time
import asyncio
import logging
import random
import json

import click
from aiokafka import AIOKafkaProducer

loop = asyncio.get_event_loop()

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


class KafkaProducerLoad:
    def __init__(self, name, n_msgs, msg_period, topic, producer_config):
        self._name = name
        self._n_msgs = n_msgs
        self._msg_period = msg_period
        self._topic = topic
        self._producer = None
        self._producer_config = producer_config

    async def run(self):
        self._producer = AIOKafkaProducer(**self._producer_config)
        await self._producer.start()
        try:
            await self._send_messages()
        finally:
            await self._producer.stop()

    async def _send_messages(self):
        for seq_num in range(self._n_msgs):
            msg = self._create_message()
            msg["sequence_number"] = seq_num
            await self._producer.send_and_wait(self._topic, json.dumps(msg).encode())
            await asyncio.sleep(self._msg_period)
            logger.info(f"{self._name}: {msg} sent")

    @staticmethod
    def _create_message():
        timenow = time.time()
        msg = {
            "id": random.choice(range(1000)),
            "timestamp": timenow,
        }
        return msg


@click.command()
@click.option("--n_producers", default=1)
@click.option("--n_messages", default=1000)
@click.option("--msgs_per_sec", default=1)
def main(n_producers, n_messages, msgs_per_sec):
    logging.basicConfig(level=logging.INFO)
    producers = []
    for prod_num in range(n_producers):
        prod = KafkaProducerLoad(
            f"prod_{prod_num}",
            topic="telemetry",
            n_msgs=n_messages,
            msg_period=1 / msgs_per_sec,
            producer_config={
                "bootstrap_servers": 'localhost:19092',
            }
        )
        producers.append(prod)

    logger.info(f"Starting {len(producers)} producers")
    logger.info(f"Number of messages to deliver: {n_messages * n_producers}")
    logger.info(f"Expected message rate: {1 / msgs_per_sec * n_producers}")

    loop.run_until_complete(
        asyncio.gather(*[prod.run() for prod in producers])
    )


main()