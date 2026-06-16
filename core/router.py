import logging
from enum import Enum

logger = logging.getLogger("AURA.router")


class Route(Enum):
    DATA = "data"
    HAIKU = "haiku"
    FULL = "full"


_DATA_TRIGGERS = {
    "plan", "plans", "schedule", "goal", "goals",
    "weather", "time", "date", "status", "open", "battery",
}

_HAIKU_TRIGGERS = {
    "hey", "hi", "hello", "how are you", "thanks",
    "cool", "nice", "morning", "night", "bye", "see ya",
}


class ResponseRouter:

    @staticmethod
    def classify(user_message: str) -> Route:
        words = set(user_message.lower().strip().split())

        if words & _DATA_TRIGGERS:
            logger.info("Route → DATA")
            return Route.DATA

        if words & _HAIKU_TRIGGERS or len(user_message) < 20:
            logger.info("Route → HAIKU")
            return Route.HAIKU

        logger.info("Route → FULL")
        return Route.FULL
