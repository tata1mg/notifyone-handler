import base64
import logging
from typing import Any, Dict, List
from urllib import parse

from aiohttp import ClientResponse

from app.commons import aws, http
from app.commons.logging.types import LogRecord
from app.constants import HTTPStatusCodes
from app.constants.channel_gateways import EmailGateways
from app.service_clients.api_handler import APIClient
from app.service_clients.callback_handler import (CallbackHandler,
                                                  CallbackLogger)
from app.services.handlers.notifier import Notifier
from app.utils import get_value_by_priority

logger = logging.getLogger()


class SparkPostHandler(Notifier, APIClient, CallbackHandler):
    __provider__ = EmailGateways.SPARK_POST.value

    BASE_URL: str = "https://api.sparkpost.com"
    ENDPOINT: str = "/api/v1/transmissions?num_rcpt_errors=3"

    def __init__(self, config: Dict) -> None:
        self.config = config
        self._headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Authorization": self.config["API_KEY"],
        }

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers.update(value)

    def _get_email_body(self, to: str, body: str, subject: str, sender: dict):
        reply_to = sender["reply_to"]
        email_from = {"email": sender["address"], "name": sender["name"]}
        recipients = []
        to = to.split(",") if isinstance(to, str) else to
        for _email_to in to:
            recipients.append({"address": _email_to})
        return {
            "recipients": recipients,
            "content": {
                "from": email_from,
                "subject": subject,
                "reply_to": reply_to,
                "html": body,
            },
        }

    def _get_url(self):
        return parse.urljoin(self.BASE_URL, self.ENDPOINT)

    async def _send_email_without_attachments(
        self, to, body, subject, sender: dict = None, **kwargs
    ):
        """
        Send email using SparkPost client API
        """
        url = self._get_url()
        payload = self._get_email_body(to, body, subject, sender)
        try:
            response = await self.request(method="post", path=url, data=payload)
            return await self.format_response(response)
        except Exception as err:
            logger.exception(
                "Encountered error while sending email %s, to %s, subject %s",
                err,
                to,
                subject,
            )
            return http.Response(
                status_code=HTTPStatusCodes.INTERNAL_ERROR.value,
                error={"error": f"Encountered error while sending email {str(err)}"},
            )

    @staticmethod
    async def format_response(response: ClientResponse):
        json = await response.json()
        if http.is_success(response.status):
            response = {
                "status_code": HTTPStatusCodes.SUCCESS.value,
                "data": {"data": json},
                "event_id": json["results"]["id"],
                "meta": json,
            }
        else:
            response = {
                "status_code": HTTPStatusCodes.BAD_REQUEST.value,
                "error": {"error": json},
                "meta": json,
            }
        return http.Response(**response)

    async def _send_email_with_attachments(
        self,
        to: str,
        body: str,
        subject: str,
        files: List[str],
        sender: dict = None,
        **kwargs,
    ):
        """
        Send email using AWS Lambda to attach files with email body
        """
        attachments = []
        for file in files:
            url = file["url"]
            filename = file["filename"]
            headers, content = await aws.get_file_details(url)
            attachment = {
                "name": filename,
                "type": headers["content-type"],
                "data": base64.b64encode(content).decode("ascii"),
            }
            attachments.append(attachment)

        payload = self._get_email_body(to, body, subject, sender)
        payload["content"]["attachments"] = attachments
        try:
            response = await self.request("POST", path=self._get_url(), data=payload)
            return await self.format_response(response)
        except Exception as err:
            logger.error(
                "Couldn't send email with attachment: %s",
                err,
            )
            return http.Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value,
                error={"error": f"Encountered error while sending email {str(err)}"},
            )

    async def send_notification(self, to: str, message: str, **kwargs):
        """
        Send email with
        """
        send_email = self._send_email_without_attachments
        if kwargs.get("files"):  # If files are to be attached
            send_email = self._send_email_with_attachments

        return await send_email(to, message, **kwargs)

    @staticmethod
    def __get_callback_status(status: str):
        status_map = {
            "bounce": "FAILED",
            "delivery": "SUCCESS",
            "injection": "SUCCESS",
            "out_of_band": "FAILED",
            "delay": "FAILED",
            "policy_rejection": "FAILED",
            "generation_failure": "FAILED",
            "generation_rejection": "FAILED",
            "open": "SUCCESS",
            "click": "SUCCESS",
        }
        return status_map.get(status, "UNKNOWN")

    @classmethod
    async def handle_callback(cls, data: Dict[str, Any]):
        AVAILABLE_KEYS = [
            "message_event",
            "track_event",
            "ingest_event",
            "gen_event",
            "relay_event",
            "ab_test_event",
            "unsubscribe_event",
        ]
        logrecord = LogRecord(log_id="-1")

        body = data.get("body")
        if not isinstance(body, list):
            body = [body]

        for data in body:
            msys = data.get("msys", {})
            message = get_value_by_priority(msys, AVAILABLE_KEYS, default={})
            type = message.get("type")
            if not isinstance(type, str):
                logger.error(
                    "status type is not of type a string for operator event_id %s",
                    message.get("transmission_id"),
                )
                continue
            status = cls.__get_callback_status(type.lower())
            response_dict = {
                "status_code": HTTPStatusCodes.SUCCESS.value,
                "event_id": message.get("transmission_id"),
                "meta": data,
            }

            if status == "SUCCESS":
                response_dict.update({"data": {"data": {"status": type}}})
            else:
                response_dict.update(
                    {
                        "error": {
                            "error": {
                                "status": type,
                                "error_code": message.get("error_code"),
                                "reason": message.get("raw_reason"),
                            }
                        }
                    }
                )
            response = http.Response(**response_dict)
            async with CallbackLogger.logger as log:
                await log.log(
                    logrecord,
                    extras={
                        "provider": cls,
                        "response": response,
                        "status": status,
                        "channel": "email",
                    },
                )
