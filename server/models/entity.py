
from datetime import datetime as Datetime

from .id import Id, create_id


def Entity(_id_source: str = None):
    class IdEntity:
        _id: Id
        _created_date: Datetime
        _updated_date: Datetime

        def __post_init__(self):
            if _id_source:
                self._id = Id(str(getattr(self, _id_source)))
            else:
                self._id = create_id()

            if not hasattr(self, "_created_date"):
                self.set_created_date()

            if not hasattr(self, "_updated_date"):
                self.set_updated_date()

        def set_created_date(self):
            self._created_date = Datetime.now()

        def set_updated_date(self):
            self._updated_date = Datetime.now()

    return IdEntity
