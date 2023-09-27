import logging

from app.constants.channel_gateways import PushGateways
from app.services.abstract_handler import AbstractHandler
from app.services.push.apns import APNSHandler
from app.services.push.fcm import FCMHandler

logger = logging.getLogger()


class PushHandler(AbstractHandler):
    CHANNEL = "push"
    HANDLER_CONFIG_KEY = "PUSH_HANDLER"
    PROVIDER_CLASS_MAPPING = {
        PushGateways.FCM.value: FCMHandler,
        PushGateways.APNS.value: APNSHandler,
    }

    @classmethod
    def handler_config_key(cls):
        return cls.HANDLER_CONFIG_KEY

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING
