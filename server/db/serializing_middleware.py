
from datetime import datetime
from typing import Callable

from pserialize import Deserializer, Serializer


def get_application_serializer():
    def serializer(obj: datetime, middleware: dict[type, Callable[[object], type]] = {}) -> str:
        return obj.isoformat()

    return Serializer(
        middleware={
            datetime: serializer
        }
    )


def get_application_deserializer():
    def deserializer(value: str, middleware: dict[type, Callable[[object], type]] = {}) -> datetime:
        return datetime.fromisoformat(value)
        
    return Deserializer(
        middleware={
            datetime: deserializer
        }
    )