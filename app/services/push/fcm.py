import json
import logging
from typing import Dict, List

from aiohttp import ContentTypeError

from app.commons import http, push
from app.constants import HTTPStatusCodes
from app.constants.channel_gateways import PushGateways
from app.service_clients.api_handler import APIClient
from app.services.notifier import Notifier

logger = logging.getLogger()


class FCMHandler(Notifier, APIClient):
    __provider__ = PushGateways.FCM.value

    HOST = "https://fcm.googleapis.com"
    ENDPOINT = "fcm/send"

    def __init__(self, config: Dict) -> None:
        self.AUTH_KEY = config.get("AUTH_KEY", "")

    @property
    def headers(self):
        return {
            "Authorization": f"key={self.AUTH_KEY}",
            "Content-Type": "application/json",
        }

    def _get_url(self):
        return f"{self.HOST}/{self.ENDPOINT}"

    def _prepare_payload(
        self, to: List[str], notification: push.Notification, **kwargs
    ):
        return {
            "registration_ids": to,
            "notification": {
                "title": notification.title,
                "body": notification.body,
                "image": notification.image,
            },
            "data": {**kwargs, "provider": "FCM"},
        }

    @staticmethod
    async def format_response(response):
        content = ""
        try:
            content = await response.json()
            event_id = content.get("multicast_id")
        except ContentTypeError:
            content = await response.text()
            logger.error("Received text response :: %s", content)
            event_id = "-1"
        if http.is_success(response.status):
            response = {
                "status_code": HTTPStatusCodes.SUCCESS.value,
                "data": {"data": content},
                "event_id": event_id,
                "meta": content,
            }
        else:
            response = {
                "status_code": HTTPStatusCodes.BAD_REQUEST.value,
                "error": {"error": content},
                "meta": content,
            }
        return http.Response(**response)

    async def push_notification(
        self, to: List[str], notification: push.Notification, **kwargs
    ):
        payload = self._prepare_payload(to, notification, **kwargs)
        try:
            response = await self.request("POST", self._get_url(), data=payload)
            return await self.format_response(response)
        except Exception as err:
            logger.exception(
                "Encountered error while sending push notification %s", err
            )
            return http.Response(
                status_code=HTTPStatusCodes.INTERNAL_ERROR.value,
                error={
                    "error": f"Encountered error while sending push noitifcation {str(err)}"
                },
            )

    async def send_notification(self, to: List[str], message: str, **kwargs):
        title = kwargs.get("title")
        image = kwargs.get("image")
        notification = push.Notification(title=title, body=message, image=image)

        return await self.push_notification(to, notification, **kwargs)
