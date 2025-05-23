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
        
    @classmethod
    def get_default_priority(cls) -> list:
        """
        Returns the default provider priority order for SMS gateways.
        This is used when no dynamic priority logic is available or when it fails.
        
        The list contains unique identifiers of gateway instances in priority order.
        """
        try:
            print("Getting default priority for SMS handler")
            print("cls.providers: %s" % cls.PROVIDERS)
            print("cls.provider_class_mapping: %s" % cls.PROVIDER_CLASS_MAPPING)
            # Get priority from handler config if available
            if cls._HANDLER_CONFIG and "default_priority" in cls._HANDLER_CONFIG:
                return cls._HANDLER_CONFIG["default_priority"]
            
            # Fallback to using available provider keys if no priority is defined
            if cls.PROVIDERS:
                print("Returning default priority from providers")
                print("cls.PROVIDERS.keys(): %s" % cls.PROVIDERS.keys())
                return list(cls.PROVIDERS.keys())
                
            # Return empty list if no providers are available
            return []
        except Exception as e:
            logger.error(f"Error getting default priority: {str(e)}")
            return []

    @classmethod
    def get_priority_logic(cls) -> str:
        """
        Returns the dynamic priority logic expression as a string.
        
        This expression will be evaluated using Python's eval() to determine
        the gateway priority order based on request parameters.
        
        Example format: "['sms_country_1', 'sms_country_2'] if data.get('event_type') == 'otp' else ['sms_country_2', 'sms_country_1']"
        """
        try:
            # Get dynamic priority logic from handler config if available
            if cls._HANDLER_CONFIG and "dynamic_priority" in cls._HANDLER_CONFIG:
                return cls._HANDLER_CONFIG["dynamic_priority"]
            
            # Return empty string if no dynamic priority logic is defined
            return ""
        except Exception as e:
            logger.error(f"Error getting priority logic: {str(e)}")
            return ""