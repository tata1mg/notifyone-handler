import logging

from app.constants import Channels
from app.constants.channel_gateways import WhatsAppGateways
from app.services.handlers.abstract_handler import AbstractHandler
from app.services.handlers.whatsapp.interakt import InteraktHandler

logger = logging.getLogger()


class WhatsappHandler(AbstractHandler):
    CHANNEL = Channels.WHATSAPP.value
    PROVIDER_CLASS_MAPPING = {WhatsAppGateways.INTERAKT.value: InteraktHandler}

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING
