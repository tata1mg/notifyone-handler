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

    @classmethod
    def get_default_priority(cls) -> list:
        """
        Returns the default provider priority order for EMAIL gateways.
        This is used when no dynamic priority logic is available or when it fails.
        
        The list contains unique identifiers of gateway instances in priority order.
        """
        try:
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
