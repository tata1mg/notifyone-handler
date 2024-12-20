from abc import ABC, abstractmethod

from app.commons import http


class Notifier(ABC):

    __provider__ = "Provider"

    @abstractmethod
    async def send_notification(self, to: str, message: str, **kwargs) -> http.Response:
        """
        This abstract method should be overridden by the provider handler
        """
        raise NotImplementedError("The method is not implemented yet!")
