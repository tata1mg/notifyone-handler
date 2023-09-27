from torpedo import Request, send_response

from app.pubsub.sqs_handler.sqs_handler import PushSqsHandler
from app.routes.push.blueprint import PushBlueprint
from app.routes.test_sqs_subs_code import test_sqs_subscribe_code

push_test_bp = PushBlueprint("test_push")


@push_test_bp.route("/test", methods=["POST"], name="test_push")
async def test_push(req: Request):
    status_code, response_data = await test_sqs_subscribe_code(req, PushSqsHandler)
    return send_response(data=response_data, status_code=status_code)
