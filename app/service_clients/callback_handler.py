from abc import ABC, abstractmethod
from typing import Any, Dict

from app.commons.logging import AsyncLoggerContextCreator


class CallbackHandler(ABC):
    @classmethod
    @abstractmethod
    async def handle_callback(cls, data: Dict[str, Any]):
        """
        Abstract method to handle callbacks
        """


class CallbackLogger:

    logger = None

    @classmethod
    def init(cls, logger: AsyncLoggerContextCreator):
        cls.logger = logger
