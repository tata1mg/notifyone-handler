import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class NoGatewayPriorityConfigured(Exception):
    """Raised when a channel has no gateway priority configured."""


class PriorityGatewaySelection(ABC):
    """
    priority_logic
    """

    @classmethod
    @abstractmethod
    def get_priority_logic(cls) -> str:
        """
        This abstract method must be overridden by the channel manager.
        """
        pass

    @classmethod
    @abstractmethod
    def get_default_priority(cls) -> list:
        """
        This abstract method must be overridden by the channel manager.
        """
        pass

    @classmethod
    def select_gateway(cls, n_attempts: int, request_data: dict) -> str:
        """
        Gateway selection for the current send request
        The logic makes use of below attributes to decide the gateway -
            1) priority logic for the channel
            2) default priority for the channel
            3) n_attempts - no of attempt for this request

        * This will be extended to use the gateways current health and other relevant parameters
        to decide the gateway in the future releases.
        * Current Logic -
            - If the priority logic is set, the gateways order is governed by the priority logic output
            - the (n_attempts)th gateway from the priority order is returned for the current request

        """
        priority_logic_expression = cls.get_priority_logic()
        default_priority = cls.get_default_priority() or []
        current_priority = list(default_priority)
        if priority_logic_expression:
            # execute the priority logic to get the priority order of gateways
            try:
                # Never delete the 'data' declaration below. It is used in the eval statement.
                data = request_data
                current_priority = eval(priority_logic_expression)
            except Exception as exc:
                logger.warning(
                    "Priority logic evaluation failed for channel %s; falling back to default priority. Error: %s",
                    cls.__name__,
                    exc,
                )
                current_priority = list(default_priority)

        if not current_priority or not default_priority:
            logger.error(
                "No gateway priority configured for channel %s; cannot select a gateway.",
                cls.__name__,
            )
            raise NoGatewayPriorityConfigured(
                f"No gateway priority configured for channel {cls.__name__}"
            )

        total_gateways = min(len(default_priority), len(current_priority))
        return current_priority[n_attempts % total_gateways]
