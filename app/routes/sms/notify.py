from sanic_openapi import openapi
from torpedo import Request, send_response

from app.commons.logging.types import LogRecord
from app.routes.sms.api_model import SmsNotifyApiModel
from app.routes.sms.blueprint import SmsBlueprint
from app.services.handlers.sms.handler import SmsHandler

sms_notify_bp = SmsBlueprint("notify_sms")


@sms_notify_bp.route(
    SmsNotifyApiModel.uri(),
    methods=[SmsNotifyApiModel.http_method()],
    name=SmsNotifyApiModel.name(),
)
@openapi.definition(
    summary=SmsNotifyApiModel.summary(),
    description=SmsNotifyApiModel.description(),
    body={
        SmsNotifyApiModel.request_content_type(): SmsNotifyApiModel.RequestBodyOpenApiModel
    },
    response={
        SmsNotifyApiModel.response_content_type(): SmsNotifyApiModel.ResponseBodyOpenApiModel
    },
)
async def notify(request: Request):
    data = request.json
    to = data.pop("to")
    message = data.pop("message")
    log_info = LogRecord(log_id=data.pop("notification_log_id", "-1"))
    provider, response = await SmsHandler.notify(to, message, log_info=log_info, **data)
    response_data = {
        "status": response.status_code,
        "message": response.data or response.error,
        "operator": {
            "name": provider.__provider__,
            "event_id": response.event_id,
        },
        "meta": response.meta,
    }
    return send_response(
        data=response_data,
        status_code=response.status_code,
    )
