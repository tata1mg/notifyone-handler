from enum import Enum


class SmsEventStatus(str, Enum):
    SENT = "SENT"
    QUEUED = "QUEUED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    OPT_OUT = "OPT_OUT"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    DELIVERED = "DELIVERED"
    UNDELIVERED = "UNDELIVERED"
    INVALID_NUMBER = "INVALID_NUMBER"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value
