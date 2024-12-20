import logging

from app.constants import Channels
from app.constants.channel_gateways import EmailGateways
from app.services.handlers.abstract_handler import AbstractHandler
from app.services.handlers.email.ses import AwsSesHandler
from app.services.handlers.email.sparkpost import SparkPostHandler

logger = logging.getLogger()


class EmailHandler(AbstractHandler):
    CHANNEL = Channels.EMAIL.value
    PROVIDER_CLASS_MAPPING = {
        EmailGateways.SPARK_POST.value: SparkPostHandler,
        EmailGateways.AWS_SES.value: AwsSesHandler,
    }

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING
