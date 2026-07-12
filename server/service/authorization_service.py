from db.daos.rbac import PermDAO, RolePermDAO, UserRoleDAO
from models.base.id import Id

from .tree_store import TreeStore


_STORE = TreeStore()
_TREE_CLASS = __import__("service." + "permission_tree", fromlist=["PermissionTree"]).PermissionTree


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
        for role_id in self._role_ids_for_user(user_id):
            role_tree = self._tree_for_role(role_id)
            if role_tree.allows(required):
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

    def _tree_for_role(self, role_id: Id | str):
        key = str(role_id)
        if key not in self.tree_store.role_tree_by_role_id:
            self.tree_store.role_tree_by_role_id[key] = self._build_tree_for_role(role_id)
        return self.tree_store.role_tree_by_role_id[key]

    def _build_tree_for_role(self, role_id: Id | str):
        role_tree = _TREE_CLASS()
        for role_perm in self.role_perm_dao.list_for_role(role_id):
            perm = self.perm_dao.get_by_id(role_perm.permission_id)
            if perm:
                role_tree.add(perm.key)
        return role_tree

    def list_access_keys(self, user_id: Id | str) -> list[str]:
        keys: list[str] = []
        for role_id in self._role_ids_for_user(user_id):
            for role_perm in self.role_perm_dao.list_for_role(role_id):
                perm = self.perm_dao.get_by_id(role_perm.permission_id)
                if perm:
                    keys.append(perm.key)
        return keys
