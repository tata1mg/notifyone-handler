import json
import logging
from typing import Any, Dict
import os
from app.commons import http
from app.commons.logging import LogRecord
from app.constants.callbacks import WhatsAppEventStatus
from app.constants.channel_gateways import WhatsAppGateways
from app.commons import execution_details as ed
from app.constants.constants import HTTPStatusCodes
from app.service_clients.api_handler import APIClient
from app.service_clients.callback_handler import (CallbackHandler,
                                                  CallbackLogger)
from app.services.handlers.notifier import Notifier

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
            "headerValues": list(template_data.get("header_values", [])),
            "buttonValues": template_data.get("button_values", {}),
        }
        attachment_data = template_data.get("attachment_data")

        if attachment_data:
            self._add_attachment_to_template(template, attachment_data)

        return template

    def _add_attachment_to_template(self, template, attachment_data):
        """Add attachment configuration to template"""
        attachments = attachment_data.get("attachments", [])
        if not attachments:
            return
        
        # Use only the first attachment
        first_attachment = str(attachments[0])
        filename = self._get_attachment_filename(attachment_data, first_attachment)
        
        template.update({
            "headerValues": attachments,
            "fileName": filename
        })

    def _get_attachment_filename(self, attachment_data, attachment_url):
        """Get filename for attachment, with fallback to generated name"""
        filename = attachment_data.get("filename")
        
        if filename:
            return filename
        
        # Generate default filename from URL extension
        file_extension = os.path.splitext(attachment_url)[1] or ".txt"
        return f"file{file_extension}"

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
            app_name = data.get('app_name')
            app_authorizations = self._config.get("APP_AUTHORIZATIONS") 
            authorization = self._config.get("AUTHORIZATION")
            authorization_key = app_authorizations.get(app_name, "DEFAULT")
            auth = authorization.get(authorization_key, authorization.get("DEFAULT"))
            self.headers = {"Authorization": auth}
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
            "message_api_sent": WhatsAppEventStatus.SENT,
            "message_api_delivered": WhatsAppEventStatus.DELIVERED,
            "message_api_read": WhatsAppEventStatus.READ,
            "message_api_failed": WhatsAppEventStatus.FAILED,
        }

        return status_mapping.get(status, WhatsAppEventStatus.UNKNOWN)

    @classmethod
    async def handle_callback(cls, data: Dict[str, Any]):
        logrecord = LogRecord(log_id="-1")
        body: Dict[str, Any] = data.get("body")
        status = body.get("type")
        data = body.get("data", {})
        message = data.get("message", {})
        detail = cls.__get_callback_status(status)

        status = ed.ExecutionDetails.map_whatsapp_status(detail)
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
                    "source": ed.ExecutionDetailsSource.WEBHOOK,
                    "detail": detail,
                },
            )
