from torpedo.constants import HTTPMethod
from sanic_openapi import openapi

from app.routes.base_api_model import BaseApiModel, File, OperatorDetails


class WhatsappNotifyApiModel(BaseApiModel):

    _uri = "/notify"
    _name = "notify_whatsapp"
    _method = HTTPMethod.POST.value
    _summary = "API to send out whatsapp notification"
    _description = (
        "This API is used by the notifyone-core to send out the `critical` priority whatsapp notifications. "
        "You can use this API to test out the send whatsapp functionality."
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
        event_type = openapi.String(
            description="Custom event type. This can be used to write priority logic",
            example="transactional",
            required=False,
        )
        notification_log_id = openapi.String(
            description="Log ID generated for this request (in notifyone-core service)",
            example="121212",
            required=True,
        )
        template = openapi.String(
            description="Whatsapp message template name in Interkt",
            example="order_details",
            required=True,
        )
        mobile = openapi.String(
            description="Recipient mobile number", example="7827XXXXXX", required=True
        )
        body_values = dict(
            description="Values for dynamic place holders in the template",
            example={"order_id": "PO112121"},
            required=False,
        )
        files: openapi.Array(
            File,
            description="List of files to be attached with the message. Currently, only 1 file attachment is supported",
            required=False,
        )

    class ResponseBodyOpenApiModel:
        status = openapi.Integer(description="Response status", example=200)
        message = openapi.String(
            description="Message", example="Whatsapp sent successfully"
        )
        operator = OperatorDetails


class WhatsappTestApiModel(BaseApiModel):

    _uri = "/test"
    _name = "test_whatsapp"
    _method = HTTPMethod.POST.value
    _summary = "API to send out whatsapp notification using SQS subscription code"
    _description = (
        "This API can be used to send out whatsapp notification using the SQS subscribe code. "
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
        event_type = openapi.String(
            description="Custom event type. This can be used to write priority logic",
            example="transactional",
            required=False,
        )
        notification_log_id = openapi.String(
            description="Log ID generated for this request (in notifyone-core service)",
            example="121212",
            required=True,
        )
        template = openapi.String(
            description="Whatsapp message template name in Interkt",
            example="order_details",
            required=True,
        )
        mobile = openapi.String(
            description="Recipient mobile number", example="7827XXXXXX", required=True
        )
        body_values = dict(
            description="Values for dynamic place holders in the template",
            example={"order_id": "PO112121"},
            required=False,
        )
        files: openapi.Array(
            File,
            description="List of files to be attached with the message. Currently, only 1 file attachment is supported",
            required=False,
        )

    class ResponseBodyOpenApiModel:
        status = openapi.Integer(description="Response status", example=200)
        message = openapi.String(
            description="Message", example="Whatsapp sent successfully"
        )
        operator = OperatorDetails
