import logging
from abc import ABC, abstractmethod
from typing import Dict

from app.commons.logging.types import AsyncLoggerContextCreator, LogRecord
from app.commons import execution_details as ed
from app.commons import http
from app.constants import HTTPStatusCodes
from app.services.handlers.gateway_priority import PriorityGatewaySelection
from app.services.handlers.notifier import Notifier
from app.service_clients.callback_handler import CallbackHandler

logger = logging.getLogger()


class AbstractHandler(PriorityGatewaySelection, ABC):
    """
    Base class for implementing the Handler class for any channel.
    For example, Handler classes for email/sms/push/whatsapp channels will extend this class
    """

    _HANDLER_CONFIG = dict()

    logger = None
    CHANNEL = None
    MAX_ATTEMPTS = None

    SOURCE = ed.ExecutionDetailsSource.INTERNAL
    PROVIDERS: Dict[str, Notifier] = {}

    @classmethod
    @abstractmethod
    def gateways_class_mapping(cls):
        """
        This abstract method must be overridden by the actual channel manager.
        """
        pass

    @classmethod
    def get_default_priority(cls) -> list:
        return cls._HANDLER_CONFIG["default_priority"]

    @classmethod
    def get_priority_logic(cls) -> str:
        return cls._HANDLER_CONFIG["dynamic_priority"]

    @classmethod
    def update_configuration(cls, handler_configuration: dict):
        cls._HANDLER_CONFIG = handler_configuration
        cls.refresh_providers()

    @classmethod
    def refresh_providers(cls):
        if not cls._HANDLER_CONFIG:
            #TODO - implement the logic to fetch the configuration from Core and set here
            return
        gateways = cls._HANDLER_CONFIG["gateways"]
        cls.ENABLED_GATEWAYS_COUNT = len(gateways)
        new_providers_map = dict()
        for gateway_config in gateways:
            unique_id = gateway_config["unique_identifier"]
            gateway = gateway_config["gateway"]
            new_providers_map[unique_id] = cls.gateways_class_mapping()[gateway](
                gateway_config["configuration"]
            )
        existing_providers_map = cls.PROVIDERS
        cls.PROVIDERS = new_providers_map
        del existing_providers_map

    @classmethod
    def initialize(cls, log: AsyncLoggerContextCreator):
        cls.refresh_providers()
        cls.logger = log

    @staticmethod
    def _get_status(provider: Notifier, response: http.Response):
        status = ed.ExecutionDetailsEventStatus.SUCCESS
        if isinstance(provider, CallbackHandler):
            status = ed.ExecutionDetailsEventStatus.QUEUED
        if response.error or (response.status_code != 200):
            status = ed.ExecutionDetailsEventStatus.FAILED
        return status

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
            status = cls._get_status(provider, response)
            async with cls.logger as log:
                await log.log(
                    log_info,
                    extras={
                        "provider": provider,
                        "response": response,
                        "sent_to": to,
                        "attempt_number": n_attempts,
                        "channel": cls.CHANNEL,
                        "source": cls.SOURCE,
                        "status": status
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
