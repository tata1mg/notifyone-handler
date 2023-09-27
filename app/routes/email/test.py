from torpedo import Request, send_response

from app.pubsub.sqs_handler.sqs_handler import EmailSqsHandler
from app.routes.email.blueprint import EmailBlueprint
from app.routes.test_sqs_subs_code import test_sqs_subscribe_code

email_test_bp = EmailBlueprint("test_email")


@email_test_bp.route("/test", methods=["POST"], name="test_email")
async def test_email(req: Request):
    status_code, response_data = await test_sqs_subscribe_code(req, EmailSqsHandler)
    return send_response(data=response_data, status_code=status_code)
