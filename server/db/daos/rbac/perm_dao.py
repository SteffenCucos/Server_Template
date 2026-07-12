from __future__ import annotations

from auth.rbac import Permission

from db.daos.entity_dao import EntityDAO
from db.repository import Repository


class PermDAO(EntityDAO[Permission]):
    def __init__(self, repository: Repository[Permission]):
        super().__init__(repository)

    def get_by_key(self, key: str) -> Permission | None:
        return self.find_one({"key": key})
