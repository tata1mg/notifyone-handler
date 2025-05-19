from enum import Enum

from app.constants.sms import SmsEventStatus


class ExecutionDetailsSource(str, Enum):
    INTERNAL = "INTERNAL"
    WEBHOOK = "WEBHOOK"


class ExecutionDetailsEventStatus(str, Enum):
    QUEUED = "QUEUED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ExecutionDetails:
    @staticmethod
    def map_status(event_status: SmsEventStatus) -> ExecutionDetailsEventStatus:
        status_map = {
            SmsEventStatus.SENT: ExecutionDetailsEventStatus.SUCCESS,
            SmsEventStatus.QUEUED: ExecutionDetailsEventStatus.QUEUED,
            SmsEventStatus.FAILED: ExecutionDetailsEventStatus.FAILED,
            SmsEventStatus.OPT_OUT: ExecutionDetailsEventStatus.FAILED,
            SmsEventStatus.EXPIRED: ExecutionDetailsEventStatus.FAILED,
            SmsEventStatus.ACCEPTED: ExecutionDetailsEventStatus.PENDING,
            SmsEventStatus.REJECTED: ExecutionDetailsEventStatus.FAILED,
            SmsEventStatus.DELIVERED: ExecutionDetailsEventStatus.SUCCESS,
            SmsEventStatus.UNDELIVERED: ExecutionDetailsEventStatus.FAILED,
            SmsEventStatus.INVALID_NUMBER: ExecutionDetailsEventStatus.FAILED,
        }

        return status_map.get(event_status, ExecutionDetailsEventStatus.SUCCESS)
