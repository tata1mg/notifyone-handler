from torpedo.constants import HTTPMethod
from sanic_openapi import openapi

from app.routes.base_api_model import BaseApiModel, File, OperatorDetails


class Sender:
    name = openapi.String(description="Sender name", example="Tata 1mg", required=True)
    address = openapi.String(
        description="Sender email address", example="xyz@1mg.com", required=True
    )
    reply_to = openapi.String(
        description="Reply to email id of sender",
        example="reply-xyz@1mg.com",
        required=True,
    )


class EmailNotifyApiModel(BaseApiModel):

    _uri = "/notify"
    _name = "notify_email"
    _method = HTTPMethod.POST.value
    _summary = "API to send out email notification"
    _description = (
        "This API is used by the notifyone-core to send out the `critical` priority email notifications. "
        "You can use this API to test out the send email functionality."
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
            description="Notification channel - `email` for email request",
            example="email",
            required=False,
        )
        notification_log_id = openapi.String(
            description="Log ID generated for this request (in notifyone-core service)",
            example="121212",
            required=True,
        )
        to = openapi.String(
            description="Recipient email ID", example="user@mail.com", required=True
        )
        message = openapi.String(
            description="text/html content for email body",
            example="Hi User <br> This is test email",
            required=True,
        )
        subject = openapi.String(
            description="Content for email subject",
            example="Test email subject",
            required=True,
        )
        sender = Sender
        event_type = openapi.String(
            description="Custom event type. This can be used to write priority logic",
            example="transactional",
            required=False,
        )
        files: openapi.Array(
            File,
            description="List of files to be attached with the email",
            required=False,
        )

    class ResponseBodyOpenApiModel:
        status = openapi.Integer(description="Response status", example=200)
        message = openapi.String(
            description="Message", example="Email sent successfully"
        )
        operator = OperatorDetails


class EmailTestApiModel(BaseApiModel):

    _uri = "/test"
    _name = "test_email"
    _method = HTTPMethod.POST.value
    _summary = "API to send out email notification using SQS subscription code"
    _description = (
        "This API can be used to send out email notification using the SQS subscribe code. "
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
            description="Notification channel - `email` for email request",
            example="email",
            required=False,
        )
        notification_log_id = openapi.String(
            description="Log ID generated for this request (in notifyone-core service)",
            example="121212",
            required=True,
        )
        to = openapi.String(
            description="Recipient email ID", example="user@mail.com", required=True
        )
        message = openapi.String(
            description="text/html content for email body",
            example="Hi User <br> This is test email",
            required=True,
        )
        subject = openapi.String(
            description="Content for email subject",
            example="Test email subject",
            required=True,
        )
        sender = Sender
        event_type = openapi.String(
            description="Custom event type. This can be used to write priority logic",
            example="transactional",
            required=False,
        )
        files: openapi.Array(
            File,
            description="List of files to be attached with the email",
            required=False,
        )

    class ResponseBodyOpenApiModel(EmailNotifyApiModel.ResponseBodyOpenApiModel):
        status = openapi.Integer(description="Response status", example=200)
        message = openapi.String(
            description="Message", example="Email sent successfully"
        )
        operator = OperatorDetails
