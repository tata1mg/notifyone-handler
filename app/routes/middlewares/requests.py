import json

from sanic import Request


class Parsers:
    @staticmethod
    def parse_form(request: Request):
        return dict(request.form)

    @staticmethod
    def parse_json(request: Request):
        return request.json

    @staticmethod
    def parse_text(request: Request):
        return request.body.decode("utf-8")


class HttpRequestParser:
    CONTENT_TYPES = {
        "application/x-www-form-urlencoded": Parsers.parse_form,
        "application/json": Parsers.parse_json,
        "text/plain": Parsers.parse_text,
    }

    @classmethod
    def parse_request(cls, request: Request):
        request.ctx.data = {
            "headers": dict(request.headers),
            "args": dict(request.args),
        }

        content_type = request.headers.get("content-type", "").lower()
        parser = cls._get_parser(content_type)
        request.ctx.data.update({"body": parser(request)})

    @classmethod
    def _get_parser(cls, content_type: str):
        for type, parser in cls.CONTENT_TYPES.items():
            # if content_type contains given key type
            if type in content_type:
                return parser
        return lambda req: None
