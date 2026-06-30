from kink import inject
from models.user.user import User

from db.config import DatabaseSettings
from db.entity_dao import EntityDAO


@inject
class UserDAO(EntityDAO[User]):
    def __init__(
        self,
        settings: DatabaseSettings | None = None,
        resource_name: str = "users",
    ):
        super().__init__(
            classType=User,
            resource_name=resource_name,
            settings=settings,
        )
