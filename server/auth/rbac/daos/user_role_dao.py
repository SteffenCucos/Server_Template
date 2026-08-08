from __future__ import annotations

from auth.rbac import UserRole
from models.base.id import Id

from db.daos.entity_dao import EntityDAO
from db.repository import Repository


class UserRoleDAO(EntityDAO[UserRole]):
    def __init__(self, repository: Repository[UserRole]):
        super().__init__(repository)

    async def list_for_user(self, user_id: Id | str) -> list[UserRole]:
        return [
            item for item in await self.list() if str(item.user_id) == str(user_id)
        ]

    async def list_for_role(self, role_id: Id | str) -> list[UserRole]:
        return [
            item for item in await self.list() if str(item.role_id) == str(role_id)
        ]
