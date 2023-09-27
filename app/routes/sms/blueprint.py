from typing import List, Optional, Union

from sanic import Blueprint


class SmsBlueprint(Blueprint):
    def __init__(
        self,
        name: str = None,
        url_prefix: Optional[str] = None,
        host: Optional[Union[List[str], str]] = None,
        version: Optional[Union[int, str, float]] = None,
        strict_slashes: Optional[bool] = None,
        version_prefix: str = "/v",
    ):
        url_prefix = url_prefix or ""
        url_prefix = "sms/" + url_prefix
        super(SmsBlueprint, self).__init__(
            name=name,
            url_prefix=url_prefix,
            host=host,
            version=version,
            strict_slashes=strict_slashes,
            version_prefix=version_prefix,
        )
