from dataclasses import dataclass
from typing import Optional


@dataclass
class Notification:
    body: str
    title: Optional[str] = None
    image: Optional[str] = None
