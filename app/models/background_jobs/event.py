from enum import Enum
from dataclasses import dataclass
import datetime
from app.models.base import Serializable


class EventType(Enum):
    ERROR = "error"
    INFO = "info"


class Event(Serializable):
    """
    Event class of Background Job.
    """

    type: str
    message: str
    date: datetime.datetime

    def __init__(
            self,
            type: str,
            message: str
    ):
        self.type = type
        self.message = message
        self.date = datetime.datetime.utcnow()


@dataclass
class EventCreate(Serializable):
    type: str
    message: str
