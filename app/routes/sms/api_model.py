from torpedo.constants import HTTPMethod
from sanic_openapi import openapi

from app.routes.base_api_model import BaseApiModel, OperatorDetails


class SmsNotifyApiModel(BaseApiModel):

    _uri = "/notify"
    _name = "notify_sms"
    _method = HTTPMethod.POST.value
    _summary = "API to send out sms notification"
    _description = (
        "This API is used by the notifyone-core to send out the `critical` priority sms notifications. "
        "You can use this API to test out the send sms functionality."
    )

    class RequestBodyOpenApiModel:
        event_id = openapi.Integer(
            example=111, required=True, description="Event ID for this request"
        )
        event_name = openapi.String(
            description="Event Name for this request",
            example="test_event",
            required=True,
        )
        app_name = openapi.String(
            description="App Name for this request", example="test_app", required=False
        )
        notification_channel = openapi.String(
            description="Notification channel - `sms` for sms request",
            example="sms",
            required=False,
        )
        notification_log_id = openapi.String(
            description="Log ID generated for this request (in notifyone-core service)",
            example="121212",
            required=True,
        )
        to = openapi.String(
            description="Recipient mobile number", example="7827XXXXXX", required=True
        )
        message = openapi.String(
            description="text content for sms body",
            example="Hello, This is a test sms",
            required=True,
        )
        event_type = openapi.String(
            description="Custom event type. This can be used to write priority logic",
            example="transactional",
            required=False,
        )

    class ResponseBodyOpenApiModel:
        status = openapi.Integer(description="Response status", example=200)
        message = openapi.String(description="Message", example="Sms sent successfully")
        operator = OperatorDetails


class SmsTestApiModel(BaseApiModel):

    _uri = "/test"
    _name = "test_sms"
    _method = HTTPMethod.POST.value
    _summary = "API to send out sms notification using SQS subscription code"
    _description = (
        "This API can be used to send out sms notification using the SQS subscribe code. "
        "Use this to test the SQS subscribe code"
    )

    class RequestBodyOpenApiModel:
        event_id = openapi.Integer(
            example=111, required=True, description="Event ID for this request"
        )
        event_name = openapi.String(
            description="Event Name for this request",
            example="test_event",
            required=True,
        )
        app_name = openapi.String(
            description="App Name for this request", example="test_app", required=False
        )
        notification_channel = openapi.String(
            description="Notification channel - `sms` for sms request",
            example="sms",
            required=False,
        )
        notification_log_id = openapi.String(
            description="Log ID generated for this request (in notifyone-core service)",
            example="121212",
            required=True,
        )
        to = openapi.String(
            description="Recipient mobile number", example="7827XXXXXX", required=True
        )
        message = openapi.String(
            description="text content for sms body",
            example="Hello, This is a test sms",
            required=True,
        )
        event_type = openapi.String(
            description="Custom event type. This can be used to write priority logic",
            example="transactional",
            required=False,
        )

    class ResponseBodyOpenApiModel:
        status = openapi.Integer(description="Response status", example=200)
        message = openapi.String(description="Message", example="Sms sent successfully")
        operator = OperatorDetails
