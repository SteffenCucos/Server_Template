from __future__ import annotations

from auth.rbac import Role

from db.daos.entity_dao import EntityDAO
from db.repository import Repository


class RoleDAO(EntityDAO[Role]):
    def __init__(self, repository: Repository[Role]):
        super().__init__(repository)

    def get_by_name(self, name: str) -> Role | None:
        return self.find_one({"name": name})
