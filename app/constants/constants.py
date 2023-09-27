from enum import Enum

X_SHARED_CONTEXT = "X-SHARED-CONTEXT"


class ListenerEventTypes(Enum):
    AFTER_SERVER_START = "after_server_start"
    BEFORE_SERVER_START = "before_server_start"
    BEFORE_SERVER_STOP = "before_server_stop"
    AFTER_SERVER_STOP = "after_server_stop"


class SMSSenderConstant(Enum):
    SMS_COUNTRY = "sms_country"
    NETCORE = "netcore"
    PLIVO = "plivo"
    AWS_SNS = "aws_sns"
    OTP_CHANNEL = "otp"
    TRANSACTIONAL_CHANNEL = "transactional"
    SMS = "sms"
    CALL = "call"


class HTTPStatusCodes(Enum):
    SUCCESS = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    TIMEOUT_ERROR = 408
