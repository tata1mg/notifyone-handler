from app.commons.http import Response
from app.constants.channel_gateways import SmsGateways
from app.constants.constants import HTTPStatusCodes, SMSSenderConstant
from app.service_clients.aws_sns_manager import AWSSNSManager
from app.services.notifier import Notifier


class SnsHandler(Notifier):

    __provider__ = SmsGateways.AWS_SNS.value

    def __init__(self, config):
        self._config = config
        AWSSNSManager.initialize(self._config)

    async def send_notification(self, to, message, **kwargs):
        attributes_config = self._config["MESSAGE_ATTRIBUTES"]
        message_attributes = dict()
        if 'sender_id' in attributes_config:
            message_attributes.update(
                {
                    "AWS.SNS.SMS.SenderID": {
                        "DataType": "String",
                        "StringValue": attributes_config["sender_id"]
                    }
                }
            )
        if 'sms_type' in attributes_config:
            message_attributes.update(
                {
                    "AWS.SNS.SMS.SMSType": {
                        "DataType": "String",
                        "StringValue": attributes_config["sms_type"]
                    }
                }
            )

        if not to.startswith("+91"):
            to = "+91" + to
        try:
            response = await AWSSNSManager.send_sms(
                phone_number=to, message=message, message_attributes=message_attributes
            )
            if (
                response
                and response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200
            ):
                if response.get("MessageId"):
                    return Response(
                        status_code=HTTPStatusCodes.SUCCESS.value,
                        data={"data": response.get("MessageId")},
                        event_id=response.get("MessageId"),
                        meta=response,
                    )
                else:
                    return Response(
                        status_code=HTTPStatusCodes.BAD_REQUEST.value,
                        error={"error": response},
                    )
        except Exception as e:
            return Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value, error={"error": e}
            )
