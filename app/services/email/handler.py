import logging

from app.constants.channel_gateways import EmailGateways
from app.services.abstract_handler import AbstractHandler
from app.services.email.ses import AwsSesHandler
from app.services.email.sparkpost import SparkPostHandler

logger = logging.getLogger()


class EmailHandler(AbstractHandler):
    CHANNEL = "email"
    HANDLER_CONFIG_KEY = "EMAIL_HANDLER"
    PROVIDER_CLASS_MAPPING = {
        EmailGateways.SPARK_POST.value: SparkPostHandler,
        EmailGateways.AWS_SES.value: AwsSesHandler,
    }

    @classmethod
    def handler_config_key(cls):
        return cls.HANDLER_CONFIG_KEY

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING
