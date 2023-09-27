from enum import Enum


class EmailGateways(Enum):

    SPARK_POST = "SPARK_POST"
    AWS_SES = "AWS_SES"


class SmsGateways(Enum):

    SMS_COUNTRY = "SMS_COUNTRY"
    PLIVO = "PLIVO"
    AWS_SNS = "AWS_SNS"


class PushGateways(Enum):

    FCM = "FCM"
    APNS = "APNS"


class WhatsAppGateways(Enum):

    INTERAKT = "INTERAKT"
