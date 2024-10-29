import asyncio
import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

import aiobotocore

from app.commons import aws, email, http
from app.constants.channel_gateways import EmailGateways
from app.services.notifier import Notifier

logger = logging.getLogger()


class AwsSesHandler(Notifier):
    __provider__ = EmailGateways.AWS_SES.value

    CHARSET = "UTF-8"
    # ENDPOINT = "http://localhost:4566"  # For local testing

    def __init__(self, config: Dict):
        self.config = config
        self.session = aiobotocore.session.get_session()

    def _get_destination(
        self, recipients: List[str], cc: List[str], bcc: List[str]
    ) -> Dict:
        destination = {"ToAddresses": recipients}

        if cc and isinstance(cc, list):
            destination.update({"CcAddresses": cc})

        if bcc and isinstance(bcc, list):
            destination.update({"BccAddresses": bcc})

        return destination

    def _get_message(self, subject: str, html_body: str, text_body: str = None) -> Dict:
        message = {
            "Body": {
                "Html": {
                    "Charset": self.CHARSET,
                    "Data": html_body,
                }
            },
            "Subject": {
                "Charset": self.CHARSET,
                "Data": subject,
            },
        }
        if text_body:
            message["Body"].update(
                {
                    "Text": {
                        "Charset": self.CHARSET,
                        "Data": text_body,
                    },
                }
            )

        return message

    async def _prepare_multipart_mime(
        self, recipients: email.Recipients, message: email.Message, sender, reply_to
    ):
        multipart_message = MIMEMultipart("mixed")
        multipart_message["Subject"] = message.subject
        multipart_message["From"] = sender
        multipart_message["To"] = ", ".join(recipients.to)

        destinations = recipients.to

        if recipients.cc:
            multipart_message["Cc"] = ", ".join(recipients.cc)
            destinations += recipients.cc
        if recipients.bcc:
            multipart_message["Bcc"] = ", ".join(recipients.bcc)
            destinations += recipients.bcc

        multipart_message.add_header("Reply-to", reply_to)

        message_body = MIMEMultipart("alternative")
        if message.text_body:
            textpart = MIMEText(
                message.text_body.encode(self.CHARSET), "plain", self.CHARSET
            )
            message_body.attach(textpart)
        if message.html_body:
            htmlpart = MIMEText(
                message.html_body.encode(self.CHARSET), "html", self.CHARSET
            )
            message_body.attach(htmlpart)

        for file in message.files:
            url = file["url"]
            filename = file["filename"]
            headers, content = await aws.get_file_details(url)
            part = MIMEApplication(content)
            part.add_header("Content-Disposition", "attachment", filename=filename)
            multipart_message.attach(part)

        multipart_message.attach(message_body)
        return multipart_message, destinations

    async def _send_raw_email_using_ses(
        self, recipients: email.Recipients, message: email.Message, sender, reply_to
    ):
        multipart_message, destinations = await self._prepare_multipart_mime(
            recipients, message, sender, reply_to
        )
        async with self.session.create_client(
            service_name="ses",
            region_name=self.config["AWS_REGION"],
            # endpoint_url=self.ENDPOINT,  # For local testing
        ) as client:
            try:
                response = await client.send_raw_email(
                    Source=sender,
                    Destinations=destinations,
                    RawMessage={"Data": multipart_message.as_string()},
                )
                return http.Response(
                    status_code=200,
                    data={"data": response},
                    event_id=response["MessageId"],
                    meta=response,
                )
            except Exception as err:
                logger.error("Encountered error while calling send_raw_email: %s", err)
                return http.Response(
                    status_code=400, error={"error": str(err)}, meta=str(err)
                )

    async def _send_email_using_ses(
        self,
        recipients: email.Recipients,
        message: email.Message,
        sender: str,
        reply_to: str,
    ):
        destination = self._get_destination(
            recipients.to, recipients.cc, recipients.bcc
        )
        message = self._get_message(
            message.subject, message.html_body, message.text_body
        )
        async with self.session.create_client(
            service_name="ses",
            region_name=self.config["AWS_REGION"],
            # endpoint_url=self.ENDPOINT,  # For local testing
        ) as client:
            try:
                response = await client.send_email(
                    Destination=destination,
                    Message=message,
                    Source=sender,
                    ReplyToAddresses=[reply_to],
                )
                return http.Response(
                    status_code=200,
                    data={"data": response},
                    event_id=response["MessageId"],
                    meta=response,
                )
            except Exception as err:
                logger.error("Encountered error while calling send_email: %s", err)
                return http.Response(
                    status_code=400, error={"error": str(err)}, meta=str(err)
                )

    async def _send_email_without_attachments(
        self,
        to: str,
        body: str,
        subject: str,
        sender: dict = None,
        **kwargs,
    ):
        sender_address = "{name}<{address}>".format(
            name=sender["name"], address=sender["address"]
        )

        cc = kwargs.get("cc")
        bcc = kwargs.get("bcc")
        recipients = email.Recipients(to, cc, bcc)
        message = email.Message(subject, html_body=body)
        try:
            return await self._send_email_using_ses(
                recipients=recipients,
                message=message,
                sender=sender_address,
                reply_to=sender["reply_to"],
            )
        except Exception as err:
            logger.exception("Couldn't send mail using AWS SES %s", err)

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
        cc = kwargs.get("cc")
        bcc = kwargs.get("bcc")

        sender_address = "{name}<{address}>".format(
            name=sender["name"], address=sender["address"]
        )

        recipients = email.Recipients(to, cc, bcc)
        message = email.Message(subject, html_body=body, files=files)
        try:
            return await self._send_raw_email_using_ses(
                recipients, message, sender=sender_address, reply_to=sender["reply_to"]
            )
        except Exception as err:
            logger.error("Couldn't send email with attachment using AWS SES: %s", err)
            return http.Response(
                status_code=400, error={"error": str(err)}, meta=str(err)
            )

    async def send_notification(self, to: str, message: str, **kwargs) -> http.Response:
        send_email = self._send_email_without_attachments
        if kwargs.get("files"):  # If files are to be attached
            send_email = self._send_email_with_attachments

        return await send_email(to, message, **kwargs)
