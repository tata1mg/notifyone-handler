from commonutils import BaseSNSWrapper


class AWSSNSManager:

    _config = None
    _sns_wrapper = None

    @classmethod
    def initialize(cls, config):
        cls._config = config
        cls._sns_wrapper = BaseSNSWrapper({"SNS": config})

    @classmethod
    async def send_sms(cls, phone_number, message, message_attributes):
        return await cls._sns_wrapper.publish_sms(message, phone_number, message_attributes=message_attributes)
