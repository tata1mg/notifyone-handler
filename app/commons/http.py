from dataclasses import dataclass
from typing import Dict, Optional, Union


@dataclass
class Response:
    status_code: Union[int, str]
    data: Optional[Dict] = None
    error: Optional[Dict] = None
    event_id: Optional[str] = None
    meta: Optional[Dict] = None

    def __post_init__(self):
        if not self.data and not self.error:
            raise Exception("data and error both can not be null")


def is_success(status_code: int):
    return 200 <= status_code <= 299
