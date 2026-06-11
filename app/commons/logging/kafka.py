import json
from dataclasses import dataclass
from typing import Dict, Optional

from app.commons import http, time
from app.commons.logging import types
from app.pubsub.kafka import KafkaWrapper
from app.services.handlers.notifier import Notifier


@dataclass
class KafkaLogRecord:
    provider: Notifier
    response: http.Response
    status: Optional[str] = None

    def __post_init__(self):
        if not self.status:
            self.status = "SUCCESS" if self.response.status_code == 200 else "FAILED"


class KafkaLogger(types.AsyncLogger):
    def __init__(self, kafka_client: KafkaWrapper) -> None:
        self.kafka_client = kafka_client

    @staticmethod
    def __construct_message(
        log: types.LogRecord, kafkarecord: KafkaLogRecord, extras: Dict = None
    ):
        extras = extras or {}
        return json.dumps(
            {
                "sent_at": time.now(as_str=True),
                "notification_log_id": log.log_id,
                "status": kafkarecord.status,
                "message": kafkarecord.response.data
                if kafkarecord.response.data
                else kafkarecord.response.error,
                "operator": kafkarecord.provider.__provider__,
                "operator_event_id": kafkarecord.response.event_id,
                "metadata": kafkarecord.response.meta,
                **extras,
            }
        )

    async def log(
        self,
        log: types.LogRecord,
        extras: Optional[Dict] = None,
    ):
        kafkarecord = KafkaLogRecord(
            extras.pop("provider"), extras.pop("response"), extras.pop("status", None)
        )
        message = self.__construct_message(log, kafkarecord, extras)
        await self.kafka_client.publish_to_kafka(payload=message)


class KafkaAioLogger(types.AsyncLoggerContextCreator):
    def __init__(self, config: Dict) -> None:
        self.logger: KafkaLogger = None
        self.queue_name = config.get("QUEUE_NAME")
        self._kafka_config = config.get("KAFKA") or {}
        self.kafka_client = KafkaWrapper({"KAFKA": self._kafka_config})
        self._client_created = False

    async def __aenter__(self) -> KafkaLogger:
        if not self._client_created:
            await self.kafka_client.get_kafka_client(self.queue_name)
            self.logger = KafkaLogger(self.kafka_client)
            self._client_created = True
        return self.logger

    async def __aexit__(self, *args):
        """
        noop
        """
