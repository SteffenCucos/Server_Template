from models.base.id import Id

from .permission_tree import PermissionTree


class TreeStore:
    def __init__(self) -> None:
        self.role_ids_by_user_id: dict[str, list[str]] = {}
        self.role_tree_by_role_id: dict[str, PermissionTree] = {}

    def invalidate_user(self, user_id: Id | str) -> None:
        self.role_ids_by_user_id.pop(str(user_id), None)

    def invalidate_role(self, role_id: Id | str) -> None:
        self.role_tree_by_role_id.pop(str(role_id), None)

    def clear(self) -> None:
        self.role_ids_by_user_id.clear()
        self.role_tree_by_role_id.clear()
