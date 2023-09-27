import re
from typing import Any, Tuple

import aiohttp

from app.constants import aws as ac


async def get_file_details(url: str, timeout: int = 30) -> Tuple[str, Any]:
    """
    Fetch s3 file content using pre-signed URL
    """
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        content = await response.content.read()
        headers = response.headers
        return headers, content
