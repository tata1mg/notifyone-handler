from sanic_openapi import openapi
from torpedo import Request, send_response

from app.pubsub.sqs_handler.sqs_handler import WhatsappSqsHandler
from app.routes.test_sqs_subs_code import test_sqs_subscribe_code
from app.routes.whatsapp.api_model import WhatsappTestApiModel
from app.routes.whatsapp.blueprint import WhatsappBlueprint

wa_test_bp = WhatsappBlueprint("test_wa")


@wa_test_bp.route(
    WhatsappTestApiModel.uri(),
    methods=[WhatsappTestApiModel.http_method()],
    name=WhatsappTestApiModel.name(),
)
@openapi.definition(
    summary=WhatsappTestApiModel.summary(),
    description=WhatsappTestApiModel.description(),
    body={
        WhatsappTestApiModel.request_content_type(): WhatsappTestApiModel.RequestBodyOpenApiModel
    },
    response={
        WhatsappTestApiModel.response_content_type(): WhatsappTestApiModel.ResponseBodyOpenApiModel
    },
)
async def test_wa(req: Request):
    status_code, response_data = await test_sqs_subscribe_code(req, WhatsappSqsHandler)
    return send_response(data=response_data, status_code=status_code)
