import asyncio
import logging

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, TopicPartition

logger = logging.getLogger(__name__)


class KafkaWrapper:

    def __init__(self, config: dict = {}):
        config = config or {}
        self._kafka_config = config.get("KAFKA") or {}
        self.bootstrap_servers = self._kafka_config.get("BOOTSTRAP_SERVERS", "localhost:9092")
        self.max_retry_attempts = self._kafka_config.get("MAX_RETRY_ATTEMPTS", 3)
        self.topic_name = None
        self.producer = None
        self._consumer = None

    async def get_kafka_client(self, topic_name: str) -> None:
        self.topic_name = topic_name
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers
        )
        await self.producer.start()

    async def publish_to_kafka(
        self,
        payload: str,
        headers: list = None,
        batch: bool = False,
    ) -> None:
        await self.producer.send_and_wait(
            self.topic_name,
            value=payload.encode("utf-8"),
            headers=headers or [],
        )

    async def subscribe_all(
        self,
        handler,
        topic_name: str,
        group_id: str,
        max_no_of_messages: int = 5,
    ) -> None:
        consumer = AIOKafkaConsumer(
            topic_name,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        self._consumer = consumer
        await consumer.start()
        retry_counts = {}
        try:
            async for msg in consumer:
                msg_key = (msg.partition, msg.offset)
                # Increment exactly once per delivery, before any handler call.
                retry_count = retry_counts.get(msg_key, 0) + 1
                retry_counts[msg_key] = retry_count
                try:
                    data = msg.value.decode("utf-8")
                    result = await handler.handle_event(data)
                    await consumer.commit()
                    retry_counts.pop(msg_key, None)
                except Exception as e:
                    # Read the already-incremented counter — do not increment again.
                    retry_count = retry_counts[msg_key]
                    if retry_count >= self.max_retry_attempts:
                        logger.error(
                            "Dead-lettering message on topic %s partition %d offset %d after %d attempts: %s",
                            topic_name,
                            msg.partition,
                            msg.offset,
                            retry_count,
                            str(e),
                        )
                        await consumer.commit()
                        retry_counts.pop(msg_key, None)
                    else:
                        # Seek back so the message is re-fetched on the next
                        # loop iteration; aiokafka.seek() is synchronous.
                        consumer.seek(
                            TopicPartition(topic_name, msg.partition), msg.offset
                        )
                        logger.exception(
                            "Error processing message from Kafka topic %s (attempt %d): %s",
                            topic_name,
                            retry_count,
                            str(e),
                        )
        finally:
            await consumer.stop()

    async def close(self) -> None:
        if self.producer is not None:
            await self.producer.stop()
            self.producer = None
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
