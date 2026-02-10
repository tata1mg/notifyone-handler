from enum import Enum

from app.constants.sms import SmsEventStatus
from app.constants.email import EmailEventStatus
from app.constants.whatsapp import WhatsAppEventStatus


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
    def map_sms_status(event_status: SmsEventStatus) -> ExecutionDetailsEventStatus:
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
    
    @staticmethod
    def map_email_status(event_status: EmailEventStatus) -> ExecutionDetailsEventStatus:
        status_map = {
            EmailEventStatus.OPENED: ExecutionDetailsEventStatus.SUCCESS,
            EmailEventStatus.REJECTED: ExecutionDetailsEventStatus.FAILED,
            EmailEventStatus.SENT: ExecutionDetailsEventStatus.SUCCESS,
            EmailEventStatus.DEFERRED: ExecutionDetailsEventStatus.PENDING,
            EmailEventStatus.DELIVERED: ExecutionDetailsEventStatus.SUCCESS,
            EmailEventStatus.BOUNCED: ExecutionDetailsEventStatus.FAILED,
            EmailEventStatus.CLICKED: ExecutionDetailsEventStatus.SUCCESS,
            EmailEventStatus.SPAM: ExecutionDetailsEventStatus.FAILED,
            EmailEventStatus.UNSUBSCRIBED: ExecutionDetailsEventStatus.FAILED,
            EmailEventStatus.DELAYED: ExecutionDetailsEventStatus.PENDING,
            EmailEventStatus.COMPLAINT: ExecutionDetailsEventStatus.FAILED,
        }

        return status_map.get(event_status, ExecutionDetailsEventStatus.SUCCESS)
    
    @staticmethod
    def map_whatsapp_status(event_status: WhatsAppEventStatus) -> ExecutionDetailsEventStatus:
        status_map = {
            WhatsAppEventStatus.SENT: ExecutionDetailsEventStatus.SUCCESS,
            WhatsAppEventStatus.DELIVERED: ExecutionDetailsEventStatus.SUCCESS,
            WhatsAppEventStatus.READ: ExecutionDetailsEventStatus.SUCCESS,
            WhatsAppEventStatus.FAILED: ExecutionDetailsEventStatus.FAILED,
        }

        return status_map.get(event_status, ExecutionDetailsEventStatus.SUCCESS)

