import json
import logging
from commonutils.handlers.sqs import SQSHandler
from sanic.log import logger

from app.commons.logging.types import LogRecord
from app.constants.error_messages import JsonDecode
from app.services.handlers.email.handler import EmailHandler
from app.services.handlers.push.handler import PushHandler
from app.services.handlers.sms.handler import SmsHandler
from app.services.handlers.whatsapp.handler import WhatsappHandler

logger = logging.getLogger()

class SMSSqsHandler(SQSHandler):
    @classmethod
    async def handle_event(cls, data):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as err:
            logger.info(JsonDecode.DECODE.value.format(err))

        to = data.pop("to")
        message = data.pop("message")
        log_info = LogRecord(log_id=data.pop("notification_log_id", "-1"))
        return await SmsHandler.notify(to, message, log_info=log_info, **data)


class EmailSqsHandler(SQSHandler):
    @classmethod
    async def handle_event(self, data):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logger.info(JsonDecode.DECODE.value.format(e))
            raise e

        log_info = LogRecord(log_id=data.pop("notification_log_id", "-1"))
        to = data.pop("to", "")
        message = data.pop("message", "")
        return await EmailHandler.notify(
            to=to, message=message, log_info=log_info, **data
        )


class WhatsappSqsHandler(SQSHandler):
    @classmethod
    async def handle_event(cls, data):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as err:
            logger.info(JsonDecode.DECODE.value.format(err))
            raise err

        log_info = LogRecord(data.pop("notification_log_id", "-1"))
        to = data.pop("mobile", "")
        return await WhatsappHandler.notify(to, data, log_info=log_info)


class PushSqsHandler(SQSHandler):
    @classmethod
    async def handle_event(cls, data):
        try:
            data = json.loads(data)
        
            log_info = LogRecord(log_id=data.get("notification_log_id"))
            data = data.pop("push_data", {})
            tokens = [
                {
                    "os": device.get("device_os_type"),
                    "voip_token": device.get("voip_token"),
                    "register_id": device.get("register_id"),
                    "device_token": device.get("device_token"),
                    "live_notification_token": device.get("live_notification_token"),
                }
                for device in data.pop("registered_devices", [])
            ]
            to = [
                token.get("register_id") for token in tokens if token.get("register_id")
            ]
            return await PushHandler.notify(
                to=tokens, message=data.get("body"), log_info=log_info, **data
            )
        except json.JSONDecodeError as err:
            logger.error("Not a valid JSON, unable to decode: %s", err)
            raise err
