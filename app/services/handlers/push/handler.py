import logging

from app.constants import Channels
from app.constants.channel_gateways import PushGateways
from app.services.handlers.abstract_handler import AbstractHandler
from app.services.handlers.push.fcm import FCMHandler
from app.services.handlers.push.fcm_v1 import FCMHandlerV1
from app.services.handlers.push.apns import APNSHandler

logger = logging.getLogger()


class PushHandler(AbstractHandler):
    CHANNEL = Channels.PUSH.value
    PROVIDER_CLASS_MAPPING = {PushGateways.FCM.value: FCMHandlerV1,
                              PushGateways.APNS.value: APNSHandler}

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING