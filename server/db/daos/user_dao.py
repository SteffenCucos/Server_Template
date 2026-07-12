from __future__ import annotations

from models.user.user import User

from db.daos.entity_dao import EntityDAO
from db.repository import Repository


class UserDAO(EntityDAO[User]):
    def __init__(self, repository: Repository[User]):
        super().__init__(repository)

    def get_by_name(self, user_name: str) -> User | None:
        return self.find_one({"user_name": user_name})

    def get_by_email(self, email: str) -> User | None:
        return self.find_one({"email": email})
