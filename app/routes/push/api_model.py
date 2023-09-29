from commonutils.constants import HTTPMethods
from sanic_openapi import openapi

from app.routes.base_api_model import BaseApiModel, OperatorDetails


class Device:
    register_id: openapi.String(
        description="Device registration ID", example="XXXXXXXXX", required=True
    )


class PushData:
    title: openapi.String(
        description="Push notification title",
        example="Test push notification",
        required=True,
    )
    body: openapi.String(
        description="Push notification body",
        example="Hi, This is test push notification",
        required=True,
    )
    target = openapi.String(description="Push notification target URL", required=False)
    image = openapi.String(description="Push notification image URL", required=False)
    registered_devices = openapi.Array(Device, required=True)


class PushNotifyApiModel(BaseApiModel):

    _uri = "/notify"
    _name = "notify_push"
    _method = HTTPMethods.POST.value
    _summary = "API to send out push notification"
    _description = (
        "This API is used by the notifyone-core to send out the `critical` priority push notifications. "
        "You can use this API to test out the send push functionality."
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
        notification_log_id = openapi.String(
            description="Log ID generated for this request (in notifyone-core service)",
            example="121212",
            required=True,
        )
        event_type = openapi.String(
            description="Custom event type. This can be used to write priority logic",
            example="transactional",
            required=False,
        )
        push_data = PushData

    class ResponseBodyOpenApiModel:
        status = openapi.Integer(description="Response status", example=200)
        message = openapi.String(
            description="Message", example="Push sent successfully"
        )
        operator = OperatorDetails


class PushTestApiModel(BaseApiModel):

    _uri = "/test"
    _name = "test_push"
    _method = HTTPMethods.POST.value
    _summary = "API to send out push notification using SQS subscription code"
    _description = (
        "This API can be used to send out push notification using the SQS subscribe code. "
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
        notification_log_id = openapi.String(
            description="Log ID generated for this request (in notifyone-core service)",
            example="121212",
            required=True,
        )
        event_type = openapi.String(
            description="Custom event type. This can be used to write priority logic",
            example="transactional",
            required=False,
        )
        push_data = PushData

    class ResponseBodyOpenApiModel:
        status = openapi.Integer(description="Response status", example=200)
        message = openapi.String(
            description="Message", example="Push sent successfully"
        )
        operator = OperatorDetails
