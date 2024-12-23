import logging

from sanic import Request
from sanic.response import json

from app.routes.middlewares.requests import HttpRequestParser
from app.routes.sms.blueprint import SmsBlueprint
from app.service_clients.callback_handler import CallbackHandler
from app.services.handlers.sms.handler import SmsHandler

logger = logging.getLogger()

sms_callback_bp = SmsBlueprint("callback_sms", url_prefix="callbacks/")


@sms_callback_bp.on_request
async def request_parser(request: Request):
    """Middleware to parse each incoming callback request according to content-type headers"""
    HttpRequestParser.parse_request(request)


@sms_callback_bp.route("/<provider_name:str>", methods=["POST"])
async def get_callback(req: Request, provider_name: str):
    provider = SmsHandler.PROVIDERS.get(provider_name)

    if not provider:
        return json({"error": f"Provider {provider_name} not found"}, status=404)

    if not isinstance(provider, CallbackHandler):
        logger.error("Given provider %s can't handle callback", provider.__provider__)
        return json(
            {"error": f"Provider {provider.__provider__} can't handle callback"},
            status=400,
        )

    await provider.handle_callback(req.ctx.data)
    return json({"data": f"Callback handled for {provider.__provider__}"}, status=200)
