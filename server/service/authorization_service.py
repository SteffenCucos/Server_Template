from db.rbac_dao import PermDAO, RolePermDAO, UserRoleDAO
from models.base.id import Id


class TreeStore:
    def __init__(self) -> None:
        self.role_ids_by_user_id: dict[str, list[str]] = {}
        self.keys_by_role_id: dict[str, list[str]] = {}


_STORE = TreeStore()


class AuthorizationService:
    def __init__(
        self,
        user_role_dao: UserRoleDAO,
        role_perm_dao: RolePermDAO,
        perm_dao: PermDAO,
        tree_store: TreeStore | None = None,
    ):
        self.user_role_dao = user_role_dao
        self.role_perm_dao = role_perm_dao
        self.perm_dao = perm_dao
        self.tree_store = tree_store or _STORE

    def user_has_access(self, user_id: Id | str, required: str) -> bool:
        required_parts = self._split(required)
        for role_id in self._role_ids_for_user(user_id):
            for key in self._keys_for_role(role_id):
                if self._matches(self._split(key), required_parts):
                    return True
        return False

    def _role_ids_for_user(self, user_id: Id | str) -> list[str]:
        key = str(user_id)
        if key not in self.tree_store.role_ids_by_user_id:
            self.tree_store.role_ids_by_user_id[key] = [
                str(user_role.role_id)
                for user_role in self.user_role_dao.list_for_user(user_id)
            ]
        return self.tree_store.role_ids_by_user_id[key]

    def _keys_for_role(self, role_id: Id | str) -> list[str]:
        key = str(role_id)
        if key not in self.tree_store.keys_by_role_id:
            result: list[str] = []
            for role_perm in self.role_perm_dao.list_for_role(role_id):
                perm = self.perm_dao.get_by_id(role_perm.permission_id)
                if perm:
                    result.append(perm.key)
            self.tree_store.keys_by_role_id[key] = result
        return self.tree_store.keys_by_role_id[key]

    def list_access_keys(self, user_id: Id | str) -> list[str]:
        keys: list[str] = []
        for role_id in self._role_ids_for_user(user_id):
            keys.extend(self._keys_for_role(role_id))
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
