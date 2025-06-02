import asyncio
import logging
import json
from typing import Dict, List, Union

from firebase_admin import messaging

from app.commons import http, push
from app.constants import HTTPStatusCodes
from app.services.handlers.notifier import Notifier
from app.service_clients.api_handler import APIClient

from .config_provider import ConfigProvider
from .credential_provider import CredentialProvider

logger = logging.getLogger(__name__)


class FCMHandlerV1(Notifier, APIClient):
    __provider__ = "Firebase Cloud Messaging V1"

    def __init__(self, config) -> None:
        self._config = config
        self._config_provider = ConfigProvider(config)
        self._credential_provider = CredentialProvider(self._config_provider)

    @staticmethod
    def get_event_ids(message_ids):
        event_ids = []
        for message_id in message_ids:
            try:
                event_id = message_id.split("/")[-1]
                event_ids.append(event_id)
            except Exception as err:
                event_ids.append(str(message_id))

        return event_ids

    @staticmethod
    def _get_android_config(push_config: dict):
        android_config = push_config.get("android_config", {})
        return messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                title=android_config.get("title"),
                body=android_config.get("message"),
                image=android_config.get("image"),
            ),
            priority=android_config.get("priority") or "high",
        )

    @staticmethod
    def _get_apns_config(push_config: dict):
        ios_config = push_config.get("ios_config", {})
        return messaging.APNSConfig(
            headers={"apns-priority": ios_config.get("priority", "10")},
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=ios_config.get("title"),
                        body=ios_config.get("body"),
                    ),
                    sound=ios_config.get("sound"),
                )
            ),
        )

    def _prepare_multicast_message(
        self, register_ids: List[str], notification: push.Notification, **kwargs
    ):
        details = kwargs.get("details")
        push_config = (details or {}).pop("config", {}) or {}
        android = None
        apns = None
        if push_config:
            android = self._get_android_config(push_config)
            apns = self._get_apns_config(push_config)
        kwargs.pop("details", None)
        if kwargs.get("type") == push.PushNotificationType.IN_APP_CALL:
            kwargs["details"] = json.dumps(details)
        message_data = {"provider": "FCM", **kwargs}
        if push_config.get("action"):
            action = json.dumps(
                push_config.get("action")
            )  # data should not contain dict
            message_data["action"] = action
        if push_config.get("target"):
            message_data["target"] = push_config.get("target")
        print(f"Message data: {message_data}")
        if message_data.get("type") == push.PushNotificationType.IN_APP_CALL:
            message_data.update(
                {
                    "title": notification.title,
                    "body": notification.body,
                    "image": notification.image,
                }
            )
            return messaging.MulticastMessage(
                tokens=register_ids,
                android=android,
                apns=apns,
                data=message_data,
            )
        print(f"MESSAGE_DATA_TEST_LOGGER: {message_data} {register_ids}")
        return messaging.MulticastMessage(
            tokens=register_ids,
            notification=messaging.Notification(
                title=notification.title,
                body=notification.body,
                image=notification.image,
            ),
            android=android,
            apns=apns,
            data=message_data,
        )

    def send_push_messages(
        self, register_ids: str, notification: push.Notification, **kwargs
    ):
        details = kwargs.get("details", None)
        print(f"Register IDs: {register_ids}")
        print(f"Notification: {notification}")
        print(f"Details: {details}")
        push_config = (details or {}).get("config", {}) or {}
        dry_run = push_config.get("dry_run", False)
        message = self._prepare_multicast_message(register_ids, notification, **kwargs)
        print(f"Message to be sent: {message}")
        print(f"Dry run: {dry_run}")
        try:
            response = messaging.send_each_for_multicast(
                message,
                dry_run=dry_run,
            )
            print(f"Response from FCM: {response}")
            message_ids = [res.message_id for res in response.responses]
            event_ids = self.get_event_ids(message_ids)
            return {
                "status_code": HTTPStatusCodes.SUCCESS.value,
                "data": {"data": event_ids},
                "meta": event_ids,
                "event_id": ",".join(event_ids),
            }

        except Exception as error:
            return {
                "status_code": HTTPStatusCodes.INTERNAL_ERROR.value,
                "error": str(error),
                "event_id": "-1",
                "meta": str(error),
            }

    def send_notification(self, to: List[str], message: str, **kwargs):
        print(f"Sending notification to: {to} with message: {message}")
        to = [
            token.get("register_id") for token in to if token.get("register_id")
        ]  # Remove empty and None register_id
        title = kwargs.get("title")
        image = kwargs.get("image")
        notification = push.Notification(title=title, body=message, image=image)
        response = self.send_push_messages(
            register_ids=to, notification=notification, **kwargs
        )
        print(response)
        return http.Response(**response)
