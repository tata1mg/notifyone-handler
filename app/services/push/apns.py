import logging
from typing import Dict, List

from app.commons import http, push
from app.constants import HTTPStatusCodes
from app.constants.channel_gateways import PushGateways
from app.service_clients.http_20_client import HTTP20Client
from app.services.notifier import Notifier

logger = logging.getLogger()


class APNSHandler(Notifier, HTTP20Client):
    __provider__ = PushGateways.APNS.value

    HOST = "https://api.push.apple.com"
    ENDPOINT = "3/device/{token}"

    def __init__(self, config: Dict) -> None:
        self.CERT = config.get("CERT", "")
        self.PRIVATE_KEY = config.get("PRIVATE_KEY", "")
        super(APNSHandler, self).__init__(cert=(self.CERT, self.PRIVATE_KEY))

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
        }

    def _get_url(self, token):
        return f"{self.HOST}/{self.ENDPOINT.format(token=token)}"

    def _prepare_payload(self, notification: push.Notification, **kwargs):
        return {
            "notification": {
                "body": notification.body,
            },
            **kwargs,
        }

    @staticmethod
    async def format_response(response):
        if http.is_success(response.status):
            response = {
                "status_code": HTTPStatusCodes.SUCCESS.value,
                "data": {"data": await response.json()},
            }
        else:
            response = {
                "status_code": HTTPStatusCodes.BAD_REQUEST.value,
                "error": {"error": await response.json()},
            }
        return http.Response(**response)

    async def push_notification(
        self, to: str, notification: push.Notification, **kwargs
    ):
        payload = self._prepare_payload(notification, **kwargs)
        try:
            response = await self.request("POST", self._get_url(to), json=payload)
            return await self.format_response(response)
        except Exception as err:
            logger.error(
                "Encountered while making request for push notification %s", err
            )
            return http.Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value,
                error={"error": f"Encountered error while sending email {str(err)}"},
            )

    async def send_notification(self, to: str, message: str, **kwargs):
        title = kwargs.get("title")
        image = kwargs.get("image")
        notification = push.Notification(title=title, body=message, image=image)

        return await self.push_notification(to, notification, **kwargs)
