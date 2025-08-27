from dataclasses import dataclass
from typing import Optional
from enum import Enum


@dataclass
class Notification:
    body: str
    title: Optional[str] = None
    image: Optional[str] = None

class PushNotificationType(str, Enum):
    BANNER = "BANNER"
    CALL = "CALL"
    LIVE_ACTIVITY = "LIVE_ACTIVITY"
    BACKGROUND = "BACKGROUND"
    IN_APP_CALL = "IN_APP_CALL"

    @classmethod
    def _missing_(cls, _value):
        return cls.BANNER


class DeviceOs(str, Enum):
    ANDROID = "android"
    IOS = "iphone os"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, _value):
        return cls.UNKNOWN