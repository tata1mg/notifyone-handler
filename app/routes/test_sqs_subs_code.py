from commonutils.handlers.sqs import SQSHandler
from torpedo import Request

from app.utils import json_dumps


async def test_sqs_subscribe_code(request: Request, handler: [SQSHandler]):
    payload = request.json or {}
    payload_json = json_dumps(payload)
    provider, response = await handler.handle_event(payload_json)
    response_data = {
        "status": response.status_code,
        "message": response.data or response.error,
        "operator": {
            "name": provider.__provider__,
            "event_id": response.event_id,
        },
        "meta": response.meta,
    }
    return response.status_code, response_data
