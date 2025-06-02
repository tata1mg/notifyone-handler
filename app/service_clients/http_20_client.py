from typing import Dict

import httpx


class HTTP20Client:
    auth = None
    params = None
    headers = None

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(http2=True)

    async def request(
        self,
        method: str,
        url: str,
        files: Dict = None,
        data: Dict = None,
        json: Dict = None,
        headers: Dict = None,
        params: Dict = None,
        auth: object = None,
    ):
        request_info = {}
        if headers or self.headers:
            request_info["headers"] = headers or self.headers
        if auth or self.auth:
            request_info["auth"] = auth or self.auth
        if params or self.params:
            request_info["params"] = params or self.params

        return await self.client.request(
            method=method, url=url, json=json, data=data, files=files, **request_info
        )
