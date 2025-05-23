import asyncio
from typing import List

from commonutils import BaseSQSWrapper
from commonutils.handlers.sqs import SQSHandler

from app.commons.logging.sqs import SQSAioLogger
from app.constants.config import Config
from app.pubsub.sqs.sms_sqs import APIClientSQS
from app.pubsub.sqs_handler.sqs_handler import (EmailSqsHandler,
                                                PushSqsHandler, SMSSqsHandler,
                                                WhatsappSqsHandler)
from app.service_clients.callback_handler import CallbackLogger
from app.services.handlers.email.handler import EmailHandler
from app.services.handlers.push.handler import PushHandler
from app.services.handlers.sms.handler import SmsHandler
from app.services.handlers.whatsapp.handler import WhatsappHandler


class Initialize:
    config = Config.get_config()
    sqs_event_mapping = {
        "SMS": {"client": APIClientSQS, "handler": SMSSqsHandler},
        "EMAIL": {"client": APIClientSQS, "handler": EmailSqsHandler},
        "PUSH": {"client": APIClientSQS, "handler": PushSqsHandler},
        "WHATSAPP": {"client": APIClientSQS, "handler": WhatsappSqsHandler},
    }

    @classmethod
    async def initialize_sqs_subscribers(cls):
        """
        Initialize only enabled subscribers here.
        Out of all the available subscribers in the code we will enable only those subscribers that are listed in the
        service config (config.ENABLED_CHANNELS list)
        """
        enabled_channels = cls.config.get("ENABLED_CHANNELS")
        if not enabled_channels:
            raise Exception("Enable at least one channel")
        for channel, callback in cls.sqs_event_mapping.items():
            if channel not in enabled_channels:
                continue
            sqs = cls.config.get("SQS", {})
            auth = cls.config.get("SQS_AUTH", {})
            channel_config = sqs.get("SUBSCRIBE", {}).get(channel, {})
            max_no_of_messages = channel_config.get("MAX_MESSAGE", 5)
            queue_name = channel_config.get("QUEUE_NAME")
            subscribers_count = channel_config.get("SUBSCRIBERS_COUNT", 1)

            sqs_handler = callback.get("handler")()

            subscribers: List[BaseSQSWrapper] = []
            for _ in range(subscribers_count):
                sqs_client = callback.get("client")({"SQS": auth})
                await sqs_client.get_sqs_client(queue_name)
                subscribers.append(sqs_client)

            cls.create_subscribers(subscribers, sqs_handler, max_no_of_messages)

    @classmethod
    def create_subscribers(
        cls, subscribers: List[BaseSQSWrapper], handler: SQSHandler, max_messages: int
    ):
        for subscriber in subscribers:
            asyncio.create_task(
                subscriber.subscribe_all(handler, max_no_of_messages=max_messages)
            )

    @classmethod
    def initialize_handlers(cls, logger):
        SmsHandler.initialize(log=logger)
        EmailHandler.initialize(log=logger)
        PushHandler.initialize(log=logger)
        WhatsappHandler.initialize(log=logger)

    @classmethod
    def initialize_callback_logger(cls, logger):
        CallbackLogger.init(logger=logger)

    @classmethod
    def initialize_service_startup_dependencies(cls):
        print("Initializing service startup dependencies")
        sqs = cls.config.get("SQS", {})
        auth = cls.config.get("SQS_AUTH", {})
        logging = sqs.get("PUBLISH", {}).get("LOGGING", {})
        logger = SQSAioLogger({"SQS": auth, **logging})

        cls.initialize_handlers(logger)
        cls.initialize_callback_logger(logger)
