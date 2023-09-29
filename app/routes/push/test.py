from sanic_openapi import openapi
from torpedo import Request, send_response

from app.pubsub.sqs_handler.sqs_handler import PushSqsHandler
from app.routes.push.api_model import PushTestApiModel
from app.routes.push.blueprint import PushBlueprint
from app.routes.test_sqs_subs_code import test_sqs_subscribe_code

push_test_bp = PushBlueprint("test_push")


@push_test_bp.route(
    PushTestApiModel.uri(),
    methods=[PushTestApiModel.http_method()],
    name=PushTestApiModel.name(),
)
@openapi.definition(
    summary=PushTestApiModel.summary(),
    description=PushTestApiModel.description(),
    body={
        PushTestApiModel.request_content_type(): PushTestApiModel.RequestBodyOpenApiModel
    },
    response={
        PushTestApiModel.response_content_type(): PushTestApiModel.ResponseBodyOpenApiModel
    },
)
async def test_push(req: Request):
    status_code, response_data = await test_sqs_subscribe_code(req, PushSqsHandler)
    return send_response(data=response_data, status_code=status_code)
