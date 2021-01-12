import time
import asyncio
import logging
import random
import json
import collections
import datetime


import blinker
import click
from aiokafka import AIOKafkaProducer

loop = asyncio.get_event_loop()

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


class MetricsStorage:
    def __init__(self):
        self._messages_sent_event_storage = collections.defaultdict(lambda: 0)

    def on_message_sent(self, worker_name):
        self._messages_sent_event_storage[worker_name] += 1

    async def print_metrics_periodically(self, period=2):
        start_time = time.time()
        while True:
            await asyncio.sleep(period)
            duration = (time.time() - start_time)
            logger.info(f"Worker statistics ({datetime.timedelta(seconds=duration)}):")
            overall_msgs_sent = 0
            overall_msgs_rate = 0
            for worker_name, messages_sent in self._messages_sent_event_storage.items():
                msgs_rate = messages_sent / duration 
                logger.info(f" -- {worker_name}: {messages_sent} msgs sent, {msgs_rate} mps")
                overall_msgs_rate += msgs_rate
                overall_msgs_sent += messages_sent
            logger.info(f" -- -- Overall: {overall_msgs_sent} msgs sent, {overall_msgs_rate} mps")

class KafkaProducerLoad:
    def __init__(self, name, n_msgs, msg_period, topic, producer_config):
        self._name = name
        self._n_msgs = n_msgs
        self._msg_period = msg_period
        self._topic = topic
        self._producer = None
        self._producer_config = producer_config

        self.message_sent = blinker.signal("message_sent")

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
            await self._producer.send(self._topic, json.dumps(msg).encode())
            self.message_sent.send(self._name)

            await asyncio.sleep(self._msg_period)
            logger.debug(f"{self._name}: {msg} sent")

    @staticmethod
    def _create_message():
        timenow = time.time()
        msg = {
            "id": random.randint(0, 1000),
            "timestamp": timenow,
        }
        return msg


@click.command()
@click.option("--n_producers", default=1)
@click.option("--n_messages", default=1000)
@click.option("--msgs_per_sec", default=1)
def main(n_producers, n_messages, msgs_per_sec):
    logging.basicConfig(level=logging.INFO)
    metrics_storage = MetricsStorage()
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
        prod.message_sent.connect(metrics_storage.on_message_sent)
        producers.append(prod)

    logger.info(f"Starting {len(producers)} producers")
    logger.info(f"Number of messages to deliver: {n_messages * n_producers}")
    logger.info(f"Expected message rate: {msgs_per_sec * n_producers}")

    loop.run_until_complete(
        asyncio.gather(
            asyncio.gather(*[prod.run() for prod in producers]),
            metrics_storage.print_metrics_periodically()
        )
    )


main()