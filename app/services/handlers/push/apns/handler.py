from typing import List, Dict

import logging

from .credential_provider import CredentialProvider

from app.commons import push, http
from app.constants import HTTPStatusCodes
from app.services.handlers.notifier import Notifier
from app.service_clients.http_20_client import HTTP20Client

logger = logging.getLogger()


class APNSHandler(Notifier, HTTP20Client):
    __provider__ = "Apple Push Noitfication Service"

    def __init__(self, config: Dict) -> None:
        self._config = config
        self.crendential_provider = CredentialProvider()
        self.host = config.get("HOST")
        self.endpoint = config.get("ENDPOINT")
        self.bundle_identifier = config.get("BUNDLE_IDENTIFIER")

        super(APNSHandler, self).__init__()

    def _get_headers(self, **kwargs):
        return {
            "Content-Type": "application/json",
            "authorization": f"bearer {self.crendential_provider.token}",
            "apns-topic": self._get_apns_topic(**kwargs),
            "apns-push-type": self._get_apns_push_type(**kwargs),
        }

    def _get_apns_topic(self, **kwargs):
        if kwargs.get("type") == push.PushNotificationType.LIVE_ACTIVITY:
            return f"{self.bundle_identifier}.push-type.liveactivity"
        return self.bundle_identifier

    def _get_apns_push_type(self, **kwargs):
        type = push.PushNotificationType(kwargs.get("type"))
        if type == push.PushNotificationType.LIVE_ACTIVITY:
            return "liveactivity"
        if type == push.PushNotificationType.BACKGROUND:
            return "background"
        return "alert"

    def _get_url(self, token):
        return f"{self.host}/{self.endpoint.format(token=token)}"

    def _prepare_payload(self, notification: push.Notification, **kwargs):
        details = kwargs.get("details") or {}
        extras = details.get("extras") or {}
        push_config = details.get("config") or {}
        ios_config = push_config.get("ios_config") or {}
        sound_not_required = push_config.get("sound", None)
        # Define the keys that are relevant for the iOS configuration
        config_keys = {
            "sound",
            "badge",
            "category",
            "content-available",
            "mutable-content",
        }

        # Extract the relevant configuration from ios_config
        config = {
            key: value
            for key, value in ios_config.items()  # noqa
            if key in config_keys
        }
        alert_payload = (
            {
                "title": notification.title,
                "body": notification.body,
            }
            if sound_not_required != -1
            else None
        )

        return {
            "aps": {
                **({"alert": alert_payload} if alert_payload else {}),
                **extras,
            },
            **config,
        }

    @staticmethod
    async def format_response(response):
        headers = response.headers
        content = str(response.content)
        if http.is_success(response.status_code):
            response = {
                "status_code": HTTPStatusCodes.SUCCESS.value,
                "data": {"data": content},
                "event_id": headers.get("apns-id"),
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
        self, token: str, notification: push.Notification, **kwargs
    ):
        payload = self._prepare_payload(notification, **kwargs)
        try:
            response = await self.request(
                "POST",
                self._get_url(token),
                json=payload,
                headers=self._get_headers(**kwargs),
            )
            return await self.format_response(response)
        except Exception as err:
            logger.exception(
                "Encountered while making request for push notification %s", err
            )
            return http.Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value,
                error={
                    "error": f"Encountered error while making request for push notification {str(err)}"
                },
                meta=str(err),
            )

    async def send_notification(self, to: List[Dict], message: str, **kwargs):
        try:
            title = kwargs.get("title")
            image = kwargs.get("image")
            notification = push.Notification(title=title, body=message, image=image)
            token = self._get_recipient(to, **kwargs)
            return await self.push_notification(token, notification, **kwargs)
        except Exception as err:
            logger.exception("Encountered while sending push notification %s", err)
            return http.Response(
                status_code=HTTPStatusCodes.BAD_REQUEST.value,
                error={
                    "error": f"Encountered error while sending push notification {str(err)}"
                },
                meta=str(err),
            )

    def _get_recipient(self, devices: List[Dict], **kwargs):
        ios_devices = list(
            filter(
                lambda device: push.DeviceOs(device.get("os")) == push.DeviceOs.IOS,
                devices,
            )
        )

        if not ios_devices:
            raise ValueError("No iOS device found in the list of devices")
        if (
            push.PushNotificationType(kwargs.get("type"))
            == push.PushNotificationType.LIVE_ACTIVITY
        ):
            details = kwargs.get("details") or {}
            activity_id = details.get("config").get("activity_id")
            device = self._get_ios_device(ios_devices, activity_id)
            return device.get("live_notification_token").get(activity_id).get("token")

        if (
            push.PushNotificationType(kwargs.get("type"))
            == push.PushNotificationType.BACKGROUND
        ):
            details = kwargs.get("details") or {}
            activity_id = details.get("config").get("activity_id")
            device = self._get_ios_device(ios_devices, activity_id)
            return device.get("device_token")

        return ios_devices[0].get("device_token") #voip token before this #changed to return the first device token if no specific activity_id is provided

    @staticmethod
    def _get_ios_device(devices, activity_id):
        """
        fetches the device with the given activity_id from the list of devices
        for the mentioned activity_id as live_notification should be sent to the same device
        """
        for device in devices:
            live_notification_token = device.get("live_notification_token") or {}
            if live_notification_token.get(activity_id) is not None:
                return device

        raise ValueError(
            f"No device found for activity_id {activity_id}, live_notification_token is missing"
        )
