from typing import Optional

from aiohttp import ClientSession, TCPConnector
from torpedo.exceptions import HTTPRequestException

from app.constants import HTTPStatusCodes
from app.utils import json_dumps


class APIClient:
    SESSION = None
    timeout: int = 30
    headers: dict = None
    auth: tuple = None
    params: dict = None

    @classmethod
    async def get_session(cls):
        if cls.SESSION is None:
            conn = TCPConnector(limit=(0), limit_per_host=(0))
            cls.SESSION = ClientSession(connector=conn)
        return cls.SESSION

    async def request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
    ):
        response = None
        request_info = {
            "url": path,
            "data": json_dumps(data),
            "json": json,
            "method": method,
            "timeout": self.timeout,
        }
        if self.headers:
            request_info["headers"] = self.headers
        if self.auth:
            request_info["auth"] = self.auth
        if self.params:
            request_info["params"] = self.params
        try:
            session = await self.get_session()
            response = await session.request(**request_info)
        except Exception as err:
            raise HTTPRequestException(
                err,
                HTTPStatusCodes.INTERNAL_ERROR.value,
                "Encountered error while making request",
            ) from err

        return response
