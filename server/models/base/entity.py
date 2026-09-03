
from datetime import datetime as Datetime

from persistence.models import PRIMARY_KEY, DEFAULT_FACTORY, field

from .id import Id, create_id


class IdEntity:
    id: Id = field(PRIMARY_KEY)
    created_date: Datetime = field(DEFAULT_FACTORY=Datetime.now)
    updated_date: Datetime = field(DEFAULT_FACTORY=Datetime.now)

    def set_created_date(self) -> None:
        self.created_date = Datetime.now()

    def set_updated_date(self) -> None:
        self.updated_date = Datetime.now()


def Entity(_id_source: str | None = None) -> type[IdEntity]:
    """
    Base Entity class that handles base fields and custom Id logic
    """
    class WiredIdEntity(IdEntity):
        def __post_init__(self) -> None:
            if _id_source:
                self.id = Id(str(getattr(self, _id_source)))
            else:
                self.id = create_id()

            if not hasattr(self, "created_date"):
                self.set_created_date()

            if not hasattr(self, "updated_date"):
                self.set_updated_date()

    return WiredIdEntity
