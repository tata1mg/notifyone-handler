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
