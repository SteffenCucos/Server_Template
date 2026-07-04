from __future__ import annotations

from auth.rbac import Permission, Role, RolePermission, UserRole
from models.base.id import Id

from db.entity_dao import EntityDAO
from db.repository import Repository


class PermDAO(EntityDAO[Permission]):
    def __init__(self, repository: Repository[Permission]):
        super().__init__(repository)

    def get_by_key(self, key: str) -> Permission | None:
        return self.find_one({"key": key})


class RoleDAO(EntityDAO[Role]):
    def __init__(self, repository: Repository[Role]):
        super().__init__(repository)

    def get_by_name(self, name: str) -> Role | None:
        return self.find_one({"name": name})


class UserRoleDAO(EntityDAO[UserRole]):
    def __init__(self, repository: Repository[UserRole]):
        super().__init__(repository)

    def list_for_user(self, user_id: Id | str) -> list[UserRole]:
        return [item for item in self.list() if str(item.user_id) == str(user_id)]

    def list_for_role(self, role_id: Id | str) -> list[UserRole]:
        return [item for item in self.list() if str(item.role_id) == str(role_id)]


class RolePermDAO(EntityDAO[RolePermission]):
    def __init__(self, repository: Repository[RolePermission]):
        super().__init__(repository)

    def list_for_role(self, role_id: Id | str) -> list[RolePermission]:
        return [item for item in self.list() if str(item.role_id) == str(role_id)]

    def list_for_perm(self, permission_id: Id | str) -> list[RolePermission]:
        return [item for item in self.list() if str(item.permission_id) == str(permission_id)]
