from typing import Dict, Optional
from enum import Enum
from commonutils.utils import CustomEnum


class MailSenderConstant(Enum):
    SparkPost = "spark_post"
    AWS_SES = "aws_ses"


class EventType(Enum):
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    OTP = "otp"
    NONE = None


class Events:
    DROPLET_APP_EVENT = "droplet"
    VACCINATION_EVENT = "diagnostic_vaccine"
    OTP_EVENT = "otp"


class EmailFrom:
    DEFAULT = "DEFAULT"
    PROMOTIONAL = "PROMOTIONAL"
    DROPLET = "DROPLET"
    DOCTOR = "DOCTOR"


class EmailHeaderName:
    TATA_1MG = "TATA_1MG"
    DROPLET = "DROPLET"


class EmailEventStatus(str, Enum):
    OPENED = "OPENED"
    REJECTED = "REJECTED"
    SENT = "SENT"
    DEFERRED = "DEFERRED"
    DELIVERED = "DELIVERED"
    BOUNCED = "BOUNCED"
    CLICKED = "CLICKED"
    SPAM = "SPAM"
    UNSUBSCRIBED = "UNSUBSCRIBED"
    DELAYED = "DELAYED"
    COMPLAINT = "COMPLAINT"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value


class EventName(CustomEnum):
    NON_PHARMA_PURCHASE_ORDERS_REPORT_TO_SUPPLIER = (
        "NON_PHARMA_PURCHASE_ORDERS_REPORT_TO_SUPPLIER"
    )
    PHARMA_PURCHASE_ORDERS_REPORT_TO_SUPPLIER = (
        "PHARMA_PURCHASE_ORDERS_REPORT_TO_SUPPLIER"
    )


class SenderDetails:
    headers = {}
    emails = {}

    @classmethod
    def initialize(cls, config: Optional[Dict] = None):
        cls.headers: Dict[str, str] = config.get("HEADER")
        cls.emails: Dict[str, str] = config.get("EMAIL")

    @classmethod
    def get(
        cls,
        app_name: Optional[str] = None,
        event_type: Optional[EventType] = None,
        event_name: Optional[str] = None,
    ):
        sender = {
            "email": EmailFrom.DEFAULT,
            "header": EmailHeaderName.TATA_1MG,
        }
        if event_name and event_name.upper() in EventName.get_all_values():
            sender["email"] = event_name.upper()
            sender["header"] = event_name.upper()
        elif app_name == Events.DROPLET_APP_EVENT:
            sender["email"] = EmailFrom.DROPLET
            sender["header"] = EmailHeaderName.DROPLET
        elif event_type == EventType.PROMOTIONAL:
            sender["email"] = EmailFrom.PROMOTIONAL

        return {
            "header": cls.headers.get(sender["header"]),
            "email": cls.emails.get(sender["email"]),
        }
