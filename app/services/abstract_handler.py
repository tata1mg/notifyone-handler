import logging
from abc import ABC, abstractmethod
from typing import Dict

from app.commons.logging.types import AsyncLoggerContextCreator, LogRecord
from app.constants import HTTPStatusCodes
from app.services.gateway_priority import PriorityGatewaySelection
from app.services.notifier import Notifier

logger = logging.getLogger()


class AbstractHandler(PriorityGatewaySelection, ABC):
    """
    Base class for implementing the Handler class for any channel.
    For example, Handler classes for email/sms/push/whatsapp channels will extend this class
    """

    logger = None
    CHANNEL = None
    MAX_ATTEMPTS = None
    DEFAULT_PRIORITY: list = None
    PRIORITY_LOGIC: str = None

    PROVIDERS: Dict[str, Notifier] = {}

    @classmethod
    @abstractmethod
    def handler_config_key(cls):
        """
        This abstract method must be overridden by the actual channel manager.
        """
        pass

    @classmethod
    @abstractmethod
    def gateways_class_mapping(cls):
        """
        This abstract method must be overridden by the actual channel manager.
        """
        pass

    @classmethod
    def get_default_priority(cls) -> list:
        return cls.DEFAULT_PRIORITY

    @classmethod
    def get_priority_logic(cls) -> str:
        return cls.PRIORITY_LOGIC

    @classmethod
    def initialize(cls, config: Dict, log: AsyncLoggerContextCreator):
        handler_config = config.get(cls.handler_config_key())

        cls.DEFAULT_PRIORITY = handler_config["DEFAULT_PRIORITY"]
        cls.PRIORITY_LOGIC = handler_config.get("PRIORITY_LOGIC") or None

        gateways = handler_config["GATEWAYS"]

        cls.ENABLED_GATEWAYS_COUNT = len(gateways.keys())

        for gateway_config in gateways.values():
            id = gateway_config["ID"]
            gateway = gateway_config["GATEWAY"]
            cls.PROVIDERS[id] = cls.gateways_class_mapping()[gateway](
                gateway_config["CONFIGURATION"]
            )
        cls.logger = log

    @classmethod
    async def notify(cls, to, message, **kwargs):
        """
        Trigger actual communication request
        ----------
            to: str
                user to which mails is needed to be sent
            message: str
                template
        """
        # If log_info is not present use log_id as `-1``
        log_info = kwargs.pop("log_info", LogRecord(log_id="-1"))
        provider, response = None, None
        for n_attempts in range(cls.ENABLED_GATEWAYS_COUNT):
            gateway = cls.select_gateway(
                n_attempts, cls._get_priority_logic_data(to, **kwargs)
            )
            provider = cls.PROVIDERS[gateway]
            response = await provider.send_notification(to, message, **kwargs)
            async with cls.logger as log:
                await log.log(
                    log_info,
                    extras={
                        "provider": provider,
                        "response": response,
                        "sent_to": to,
                        "attempt_number": n_attempts,
                        "channel": cls.CHANNEL,
                    },
                )
            if response.status_code == HTTPStatusCodes.SUCCESS.value:
                logger.info(
                    "Successfully sent %s using %s" % (cls.CHANNEL, provider.__class__.__name__)
                )
                break
            else:
                logger.error(
                    "Couldn't send %s using %s provider" % (cls.CHANNEL, provider.__class__.__name__)
                )
        return provider, response

    @classmethod
    def _get_priority_logic_data(cls, to, **kwargs):
        return {
            "to": to,
            "app_name": kwargs.get("app_name"),
            "event_id": kwargs.get("event_id"),
            "event_name": kwargs.get("event_name"),
            "event_type": kwargs.get("event_type"),
        }
