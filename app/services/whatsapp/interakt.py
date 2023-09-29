import json
import logging
import os
from typing import Any, Dict

from app.commons import http
from app.commons.logging import LogRecord
from app.constants.channel_gateways import WhatsAppGateways
from app.constants.constants import HTTPStatusCodes
from app.service_clients.api_handler import APIClient
from app.service_clients.callback_handler import (CallbackHandler,
                                                  CallbackLogger)
from app.services.notifier import Notifier

logger = logging.getLogger()


class InteraktHandler(Notifier, APIClient, CallbackHandler):
    __provider__ = WhatsAppGateways.INTERAKT.value

    def __init__(self, config):
        self._config = config
        self._headers = {"Content-Type": "application/json"}

    @property
    def headers(self) -> dict:
        return self._headers

    @headers.setter
    def headers(self, value: dict):
        self._headers.update(value)

    def _get_url(self) -> str:
        """
        Create the URL for interakt from config
        """
        interakt_host = self._config.get("HOST")
        interakt_path = self._config.get("PATH")
        return interakt_host + interakt_path

    def _get_payload(self, phone_number, data):
        """
        This will prepare the payload for sending whatsapp communication using interakt from data given.
        @param data: The dict containing data for preparing payload.
        """
        # NOTE fullPhoneNumber is phone_number with country code
        if not phone_number.startswith("+91"):
            phone_number = "+91" + phone_number

        template = self._get_template(template_data=data)
        payload = {
            "fullPhoneNumber": phone_number,
            "type": "Template",
            "template": template,
        }
        return payload

    def _get_template(self, template_data):
        """
        This is used to get the template required for sending whatsapp messages.
        @template_data: dict containing template, attachment_data (optional),bodyValues etc.
        """
        name_and_language_code_data = self._get_name_and_language_code(
            template=template_data.get("template", "")
        )
        template = {
            "name": name_and_language_code_data.get("name"),
            "languageCode": name_and_language_code_data.get("language_code"),
            "bodyValues": list(template_data.get("body_values")),
        }

        files = template_data.get("files") or list()

        if files:
            # NOTE only one file attachment is sent at time.
            file = files[0]
            attachments = [file["url"]]
            filename = file["filename"]
            template.update({"headerValues": attachments, "fileName": filename})

        return template

    @staticmethod
    def _get_name_and_language_code(template: str):
        """
        This is used to get name , language_code from template given
        Example template = 'template_name:en'
        then here name is template_name and en is language_code
        in case template does not have language_code then default en will be used
        @param template: a str template containing : separated name and language_code
        @return a dict containing name,language_code
        """
        template = template.split(":")

        # default language_code is 'en'
        language_code = "en"

        # CASE language_code provided in template.
        if len(template) > 1:
            language_code = template[1]

        return {"name": template[0], "language_code": language_code}

    async def send_notification(self, to: str, data: Dict, **kwargs) -> http.Response:
        """
        This will send whatsapp messages based on data given.
        @param data : A dict containing template(name:language_code),template body_values.
        @return A Response dict containing status_code,message,id,result etc.
        """
        try:
            self.headers = {"Authorization": self._config.get("AUTHORIZATION")}
            payload = self._get_payload(phone_number=to, data=data)
            send_whatsapp_message_url = self._get_url()
            response = await self.request(
                method="post",
                path=send_whatsapp_message_url,
                data=payload,
            )
            response_status = response.status
            response_text = await response.text()
            response = json.loads(response_text)
            response.update({"status_code": response_status})
            if not str(response_status).startswith("20"):
                return http.Response(
                    status_code=HTTPStatusCodes.BAD_REQUEST.value,
                    error={"error": response},
                    meta=response,
                )
            return http.Response(
                status_code=HTTPStatusCodes.SUCCESS.value,
                data={"data": response},
                event_id=response["id"],
                meta=response,
            )
        except Exception as err:
            logger.exception(
                "Encountered error while sending WhatsApp communication %s", err
            )
            return http.Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value,
                error={"error": str(err)},
            )

    @staticmethod
    def __get_callback_status(status: str):
        status_mapping = {
            "message_api_sent": "SUCCESS",
            "message_api_delivered": "SUCCESS",
            "message_api_read": "SUCCESS",
            "message_api_failed": "FAILED",
        }

        return status_mapping.get(status, "UNKNOWN")

    @classmethod
    async def handle_callback(cls, data: Dict[str, Any]):
        logrecord = LogRecord(log_id="-1")
        body: Dict[str, Any] = data.get("body")
        status = body.get("type")
        data = body.get("data", {})
        message = data.get("message", {})
        status = cls.__get_callback_status(status)

        response = http.Response(
            status_code=200,
            data={
                "data": {
                    "status": message.get("message_status"),
                    "failure_reason": message.get("channel_failure_reason"),
                }
            },
            event_id=message.get("id"),
            meta=data,
        )

        async with CallbackLogger.logger as log:
            await log.log(
                logrecord,
                extras={
                    "provider": cls,
                    "response": response,
                    "status": status,
                    "channel": "whatsapp",
                },
            )
