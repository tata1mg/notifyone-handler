import logging

from app.constants.channel_gateways import WhatsAppGateways
from app.services.handlers.abstract_handler import AbstractHandler
from app.services.handlers.whatsapp.interakt import InteraktHandler

logger = logging.getLogger()


class WhatsappHandler(AbstractHandler):
    CHANNEL = "whatsapp"
    HANDLER_CONFIG_KEY = "WHATSAPP_HANDLER"
    PROVIDER_CLASS_MAPPING = {WhatsAppGateways.INTERAKT.value: InteraktHandler}

    @classmethod
    def handler_config_key(cls):
        return cls.HANDLER_CONFIG_KEY

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING
