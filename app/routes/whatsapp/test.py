from torpedo import Request, send_response

from app.pubsub.sqs_handler.sqs_handler import WhatsappSqsHandler
from app.routes.test_sqs_subs_code import test_sqs_subscribe_code
from app.routes.whatsapp.blueprint import WhatsappBlueprint

wa_test_bp = WhatsappBlueprint("test_wa")


@wa_test_bp.route("/test", methods=["POST"], name="test_wa")
async def test_wa(req: Request):
    status_code, response_data = await test_sqs_subscribe_code(req, WhatsappSqsHandler)
    return send_response(data=response_data, status_code=status_code)
