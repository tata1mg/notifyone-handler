import logging

from app.constants import Channels
from app.constants.channel_gateways import SmsGateways
from app.services.handlers.abstract_handler import AbstractHandler
from app.services.handlers.sms.plivo_manager import PlivoHandler
from app.services.handlers.sms.sms_country_manager import SMSCountryHandler
from app.services.handlers.sms.sns_manager import SnsHandler

logger = logging.getLogger()


class SmsHandler(AbstractHandler):
    CHANNEL = Channels.SMS.value
    PROVIDER_CLASS_MAPPING = {
        SmsGateways.SMS_COUNTRY.value: SMSCountryHandler,
        SmsGateways.PLIVO.value: PlivoHandler,
        SmsGateways.AWS_SNS.value: SnsHandler,
    }

    @classmethod
    def gateways_class_mapping(cls):
        return cls.PROVIDER_CLASS_MAPPING
