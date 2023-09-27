from sanic import Request, json

from app.commons.logging.types import LogRecord
from app.routes.whatsapp.blueprint import WhatsappBlueprint
from app.services.whatsapp.handler import WhatsappHandler

wa_notify_bp = WhatsappBlueprint("notify_wa")


@wa_notify_bp.route("/notify", methods=["POST"])
async def notify(request: Request):
    data = request.json
    to = data.pop("to")
    message = data.pop("message")
    log_info = LogRecord(log_id=data.pop("notification_log_id", "-1"))

    provider, response = await WhatsappHandler.notify(
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
