import aiobotocore


class AWSSNSManager:

    _sns_client = None

    @classmethod
    def initialize(cls, config):
        region_name = config['AWS_SNS']['REGION_NAME']
        service_name = config['AWS_SNS']['SERVICE_NAME']
        session = aiobotocore.session.get_session()
        cls._sns_client = session.create_client(service_name=service_name, region_name=region_name)

    @classmethod
    async def send_sms(cls, phone_number, message, message_attributes):
        return (await cls._sns_client.publish(
            PhoneNumber=phone_number,
            Message=message,
            MessageAttributes=message_attributes
        ))

