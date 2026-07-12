from __future__ import annotations

from auth.rbac import RolePermission
from models.base.id import Id

from db.daos.entity_dao import EntityDAO
from db.repository import Repository


class RolePermDAO(EntityDAO[RolePermission]):
    def __init__(self, repository: Repository[RolePermission]):
        super().__init__(repository)

    def list_for_role(self, role_id: Id | str) -> list[RolePermission]:
        return [item for item in self.list() if str(item.role_id) == str(role_id)]

    def list_for_perm(self, permission_id: Id | str) -> list[RolePermission]:
        return [item for item in self.list() if str(item.permission_id) == str(permission_id)]
