import logging

from app.constants import Channels
from app.constants.channel_gateways import PushGateways
from app.services.handlers.abstract_handler import AbstractHandler
from app.services.handlers.push.fcm import FCMHandler

logger = logging.getLogger()


class PushHandler(AbstractHandler):
    CHANNEL = Channels.PUSH.value
    PROVIDER_CLASS_MAPPING = {PushGateways.FCM.value: FCMHandler}

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING
