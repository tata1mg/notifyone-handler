import logging

from app.constants.channel_gateways import SmsGateways
from app.services.abstract_handler import AbstractHandler
from app.services.sms.plivo_manager import PlivoHandler
from app.services.sms.sms_country_manager import SMSCountryHandler
from app.services.sms.sns_manager import SnsHandler

logger = logging.getLogger()


class SmsHandler(AbstractHandler):
    CHANNEL = "sms"
    HANDLER_CONFIG_KEY = "SMS_HANDLER"
    PROVIDER_CLASS_MAPPING = {
        SmsGateways.SMS_COUNTRY.value: SMSCountryHandler,
        SmsGateways.PLIVO.value: PlivoHandler,
        SmsGateways.AWS_SNS.value: SnsHandler,
    }

    @classmethod
    def handler_config_key(cls):
        return cls.HANDLER_CONFIG_KEY

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING
