from typing import Dict

import httpx


class HTTP20Client:
    def __init__(self, cert=None, verify=None) -> None:
        self.client = httpx.AsyncClient(http2=True, cert=cert, verify=verify)

    async def request(
        self,
        method: str,
        url: str,
        files: Dict = None,
        data: Dict = None,
        json: Dict = None,
    ):
        if data is not None and json is not None:
            raise ValueError("data and json both can not be not null")

        async with self.client as client:
            return await client.request(
                method=method, url=url, json=json, data=data, files=files
            )
