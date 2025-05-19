import json
from dataclasses import dataclass
from typing import Dict, Optional

from app.commons import http, time
from app.commons.logging import types
from app.commons import execution_details as ed
from app.pubsub.sqs import APIClientSQS
from app.services.handlers.notifier import Notifier


@dataclass
class SQSLogRecord:
    provider: Notifier
    response: http.Response
    status: Optional[ed.ExecutionDetailsSource] = None

    def __post_init__(self):
        if not self.status:
            self.status = (
                ed.ExecutionDetailsEventStatus.SUCCESS
                if self.response.status_code == 200
                else ed.ExecutionDetailsEventStatus.FAILED
            )

class SQSLogger(types.AsyncLogger):
    def __init__(self, sqs_client: APIClientSQS) -> None:
        self.sqs_client = sqs_client

    @staticmethod
    def __construct_message(
        log: types.LogRecord, sqsrecord: SQSLogRecord, extras: Dict = None
    ):
        extras = extras or {}
        return json.dumps(
            {
                "sent_at": time.now(as_str=True),
                "notification_log_id": log.log_id,
                "status": sqsrecord.status,
                "message": sqsrecord.response.data
                if sqsrecord.response.data
                else sqsrecord.response.error,
                "operator": sqsrecord.provider.__provider__,
                "operator_event_id": sqsrecord.response.event_id,
                "metadata": sqsrecord.response.meta,
                **extras,
            }
        )

    async def log(
        self,
        log: types.LogRecord,
        extras: Optional[Dict] = None,
    ):
        sqsrecord = SQSLogRecord(
            extras.pop("provider"), extras.pop("response"), extras.pop("status", None)
        )
        message = self.__construct_message(log, sqsrecord, extras)
        await self.sqs_client.publish_to_sqs(payload=message, batch=False)


class SQSAioLogger(types.AsyncLoggerContextCreator):
    def __init__(self, config: Dict) -> None:
        self.logger: SQSLogger = None
        self.queue_name = config.get("QUEUE_NAME")
        self.sqs_client = APIClientSQS(config)

        self._client_created = False

    async def __aenter__(self) -> SQSLogger:
        if not self._client_created:
            await self.sqs_client.get_sqs_client(self.queue_name)
            self.logger = SQSLogger(self.sqs_client)
            self._client_created = True

        return self.logger

    async def __aexit__(self, *args):
        """
        noop
        """
