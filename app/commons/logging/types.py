from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class LogRecord:
    log_id: str


class Logger(ABC):
    @abstractmethod
    def log(self, log: LogRecord, extras: Optional[Dict] = None):
        """
        Abstract method to be called by any logger to log the message
        """


class AsyncLogger(Logger, ABC):
    @abstractmethod
    async def log(self, log: LogRecord, extras: Optional[Dict] = None):
        """
        Abstract method to be called by any logger to log the message
        """


class AsyncLoggerContextCreator(ABC):
    async def __aenter__(self) -> AsyncLogger:
        """
        Async context manager method to return instance of AsyncLogger
        """

    async def __aexit__(self, *args):
        """
        Async context manager method to operator while exiting from context manager
        """
