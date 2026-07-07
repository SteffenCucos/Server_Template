from db.rbac_dao import PermDAO, RolePermDAO, UserRoleDAO
from models.base.id import Id


class AuthorizationService:
    def __init__(
        self,
        user_role_dao: UserRoleDAO,
        role_perm_dao: RolePermDAO,
        perm_dao: PermDAO,
    ):
        self.user_role_dao = user_role_dao
        self.role_perm_dao = role_perm_dao
        self.perm_dao = perm_dao

    def user_has_access(self, user_id: Id | str, required: str) -> bool:
        required_parts = self._split(required)
        for key in self.list_access_keys(user_id):
            if self._matches(self._split(key), required_parts):
                return True
        return False

    def list_access_keys(self, user_id: Id | str) -> list[str]:
        keys: list[str] = []
        for user_role in self.user_role_dao.list_for_user(user_id):
            for role_perm in self.role_perm_dao.list_for_role(user_role.role_id):
                perm = self.perm_dao.get_by_id(role_perm.permission_id)
                if perm:
                    keys.append(perm.key)
        return keys

    def _matches(self, pattern: list[str], required: list[str]) -> bool:
        for index, part in enumerate(pattern):
            if part == "**":
                return True
            if index >= len(required):
                return False
            if part != "*" and part != required[index]:
                return False
        return len(pattern) == len(required)

    def _split(self, value: str) -> list[str]:
        return [part for part in value.strip("/").split("/") if part]
