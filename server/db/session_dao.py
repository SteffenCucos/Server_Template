from auth.session.session import Session
from kink import inject

from db.config import DatabaseSettings
from db.entity_dao import EntityDAO


@inject
class SessionDAO(EntityDAO[Session]):
    def __init__(
        self,
        settings: DatabaseSettings | None = None,
        resource_name: str = "sessions",
    ):
        super().__init__(
            classType=Session,
            resource_name=resource_name,
            settings=settings,
        )
