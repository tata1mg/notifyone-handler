import logging
import re
from typing import Any, Dict

from app.commons.http import Response
from app.commons.logging import LogRecord
from app.constants.channel_gateways import SmsGateways
from app.commons import execution_details as ed
from app.constants import sms as sc
from app.constants.constants import HTTPStatusCodes, SMSSenderConstant
from app.service_clients.api_handler import APIClient
from app.service_clients.callback_handler import (CallbackHandler,
                                                  CallbackLogger)
from app.services.handlers.notifier import Notifier

logger = logging.getLogger()


class SMSCountryHandler(Notifier, APIClient, CallbackHandler):
    __provider__ = SmsGateways.SMS_COUNTRY.value

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get("TIMEOUT")

    async def send_notification(self, to, message, **kwargs):
        url = self.config.get("SMS_COUNTRY_URL")
        channel = kwargs.get("channel")
        if channel == SMSSenderConstant.OTP_CHANNEL.value:
            values = self.get_otp_channel_values(to, message)
        else:
            values = self.get_transactional_channel_values(to, message)
        try:
            response = await self.request("POST", url, data=values)
            result = await response.text()
            await response.release()
            if str(response.status).startswith("20"):
                response.job_id = self.extract_job_id(result)
                if response.job_id is not None:
                    return Response(
                        status_code=HTTPStatusCodes.SUCCESS.value,
                        data={"data": result},
                        event_id=response.job_id,
                        meta=result,
                    )
            return Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value,
                error={"error": result},
                meta=result,
            )
        except Exception as err:
            logger.error(
                "Encountered error while sending SMS using SMSCountry: %s", err
            )
            return Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value,
                error={"error": str(err)},
                meta=str(err),
            )

    def get_otp_channel_values(self, to, body):
        return {
            "User": self.config.get("SMS_COUNTRY_OTP_USERNAME"),
            "passwd": self.config.get("SMS_COUNTRY_OTP_PASSWORD"),
            "message": body,
            "mobilenumber": to,
            "mtype": "N",
            "DR": "Y",
            "sid": self.config.get("SMS_COUNTRY_OTP_SENDER_ID"),
        }

    def get_transactional_channel_values(self, to, body):
        return {
            "User": self.config.get("SMS_COUNTRY_USERNAME"),
            "passwd": self.config.get("SMS_COUNTRY_PASSWORD"),
            "message": body,
            "mobilenumber": to,
            "mtype": "N",
            "DR": "Y",
            "sid": self.config.get("SMS_COUNTRY_SENDER_ID"),
        }

    @staticmethod
    def extract_job_id(text: str):
        match = re.findall(r"^OK:(\d+)$", text)
        if len(match) == 1:
            return match[0]
        return None

    @staticmethod
    def __get_callback_status(status: int):
        """
        SMSCountry Callback status
        0 - Message In Queue
        1 - Submitted To Carrier
        2 - Un Delivered
        3 - Delivered
        4 - Expired
        8 - Rejected
        9 - Message Sent
        10 - Opted Out Mobile Number
        11 - Invalid Mobile Number
        """

        status_map = {
            0: sc.SmsEventStatus.QUEUED,
            1: sc.SmsEventStatus.ACCEPTED,
            2: sc.SmsEventStatus.UNDELIVERED,
            3: sc.SmsEventStatus.DELIVERED,
            4: sc.SmsEventStatus.EXPIRED,
            8: sc.SmsEventStatus.REJECTED,
            9: sc.SmsEventStatus.SENT,
            10: sc.SmsEventStatus.OPT_OUT,
            11: sc.SmsEventStatus.INVALID_NUMBER,
        }

        return status_map.get(int(status), sc.SmsEventStatus.UNKNOWN)

    @classmethod
    async def handle_callback(cls, data: Dict[str, Any]):
        logrecord = LogRecord(log_id="-1")
        args = data.get("args")
        status = args.get("status")[0]
        response = Response(
            status_code=200,
            data={"data": {"status": status}},
            event_id=args.get("jobno")[0],
            meta=data,
        )

        detail = cls.__get_callback_status(status)
        status = ed.ExecutionDetails.map_status(detail)
        async with CallbackLogger.logger as log:
            await log.log(
                logrecord,
                extras={
                    "provider": cls,
                    "response": response,
                    "status": status,
                    "channel": "sms",
                    "source": ed.ExecutionDetailsSource.WEBHOOK,
                    "detail": detail,
                },
            )
