from torpedo import Request, send_response

from app.pubsub.sqs_handler.sqs_handler import SMSSqsHandler
from app.routes.sms.blueprint import SmsBlueprint
from app.routes.test_sqs_subs_code import test_sqs_subscribe_code

sms_test_bp = SmsBlueprint("test_sms")


@sms_test_bp.route("/test", methods=["POST"], name="test_sms")
async def test_sms(req: Request):
    status_code, response_data = await test_sqs_subscribe_code(req, SMSSqsHandler)
    return send_response(data=response_data, status_code=status_code)
