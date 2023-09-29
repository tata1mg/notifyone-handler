from typing import Any, Dict

from aiohttp import BasicAuth

from app.commons.http import Response
from app.commons.logging import LogRecord
from app.constants.channel_gateways import SmsGateways
from app.constants.constants import HTTPStatusCodes
from app.service_clients.api_handler import APIClient
from app.service_clients.callback_handler import (CallbackHandler,
                                                  CallbackLogger)
from app.services.notifier import Notifier


class PlivoHandler(Notifier, APIClient, CallbackHandler):
    __provider__ = SmsGateways.PLIVO.value

    CALL_STATUS = {
        "ringing": 1,
        "in-progress": 2,
        "busy": 3,
        "completed": 4,
        "failed": 5,
        "timeout": 6,
        "no-answer": 7,
    }

    def __init__(self, config):
        self._config = config
        self._headers = {"content-type": "application/json"}
        self._auth = None
        self._timeout = None

    @property
    def headers(self) -> dict:
        return self._headers

    @headers.setter
    def headers(self, value: dict):
        self._headers.update(value)

    @property
    def auth(self) -> BasicAuth:
        return self._auth

    @auth.setter
    def auth(self, value: tuple):
        self._auth = BasicAuth(*value)

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        self._timeout = value

    @staticmethod
    def extract_job_id(result: dict):
        job_id = result.get("message_uuid", None)
        if not isinstance(job_id, list):
            return None
        return job_id[0]

    async def send_notification(self, to, message, **kwargs):
        url = self._config["PLIVO_SMS_URL"]
        auth_token = self._config["PLIVO_AUTH_TOKEN"]
        auth_id = self._config["PLIVO_AUTH_ID"]
        callback_url = self._config["PLIVO_CALLBACK_URL"]
        self.timeout = self._config["TIMEOUT"]
        self.auth = (auth_id, auth_token)
        url = url.format(auth_id=auth_id)
        values = {
            "src": self._config["PLIVO_SENDER_ID"],
            "dst": "+91" + to,
            "text": message,
            "url": callback_url,
            "method": "POST",
        }

        try:
            response = await self.request(method="POST", path=url, data=values)
            result = await response.json()
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
            return Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value,
                error={"error": str(err)},
                meta=str(err),
            )

    @staticmethod
    def __get_callback_status(status: str):
        status_map = {
            "queued": "SUCCESS",
            "sent": "SUCCESS",
            "failed": "FAILED",
            "delivered": "SUCCESS",
            "undelivered": "FAILED",
            "rejected": "FAILED",
        }

        return status_map.get(status, "UNKNOWN")

    @classmethod
    async def handle_callback(cls, data: Dict[str, Any]):
        logrecord = LogRecord(log_id="-1")
        body = data.get("body")
        status = body.get("Status")[0]
        if isinstance(status, str):
            status = cls.__get_callback_status(status.lower())
        response_dict = {
            "status_code": HTTPStatusCodes.SUCCESS.value,
            "event_id": body.get("MessageUUID")[0],
            "meta": data,
        }
        if status == "SUCCESS":
            response_dict.update({"data": {"data": {"status": body.get("Status")[0]}}})
        else:
            response_dict.update(
                {
                    "error": {
                        "error": {
                            "status": body.get("Status")[0],
                            "error_code": body.get("ErrorCode")[0],
                        }
                    }
                }
            )
        response = Response(**response_dict)
        async with CallbackLogger.logger as log:
            await log.log(
                logrecord,
                extras={
                    "provider": cls,
                    "response": response,
                    "status": status,
                    "channel": "sms",
                },
            )
