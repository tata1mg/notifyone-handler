from sanic import Request, json
from sanic_openapi import openapi

from app.commons.logging.types import LogRecord
from app.routes.push.api_model import PushNotifyApiModel
from app.routes.push.blueprint import PushBlueprint
from app.services.handlers.push.handler import PushHandler

push_notify_bp = PushBlueprint("notify_push")


@push_notify_bp.route(
    PushNotifyApiModel.uri(),
    methods=[PushNotifyApiModel.http_method()],
    name=PushNotifyApiModel.name(),
)
@openapi.definition(
    summary=PushNotifyApiModel.summary(),
    description=PushNotifyApiModel.description(),
    body={
        PushNotifyApiModel.request_content_type(): PushNotifyApiModel.RequestBodyOpenApiModel
    },
    response={
        PushNotifyApiModel.response_content_type(): PushNotifyApiModel.ResponseBodyOpenApiModel
    },
)
async def notify(request: Request):
    data = request.json
    to = data.pop("to")
    message = data.pop("body")
    log_info = LogRecord(log_id=data.get("notification_log_id"))
    registration_ids = []
    for device in data.pop("registered_devices", []):
        registration_ids.append(device.get("register_id"))

    provider, response = await PushHandler.notify(
        to, message, log_info=log_info, **data
    )

    return json(
        {
            "status": response.status_code,
            "message": response.data or response.error,
            "operator": {
                "name": provider.__provider__,
                "event_id": response.event_id,
            },
            "meta": response.meta,
        },
        status=response.status_code,
    )
