from auth.rbac import Permission as P
from auth.rbac import RolePermission as RP
from auth.rbac import UserRole as UR
from models.base.id import Id
from service.authorization_service import AuthorizationService
from service.permission_tree import PermissionTree
from service.tree_store import TreeStore


class UDao:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    def list_for_user(self, user_id):
        self.calls += 1
        return [row for row in self.rows if str(row.user_id) == str(user_id)]


class RDao:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    def list_for_role(self, role_id):
        self.calls += 1
        return [row for row in self.rows if str(row.role_id) == str(role_id)]


class PDao:
    def __init__(self, rows):
        self.rows = {str(row._id): row for row in rows}
        self.calls = 0

    def get_by_id(self, row_id):
        self.calls += 1
        return self.rows.get(str(row_id))


def test_role_store_no_reload_on_no_match():
    user_id = Id("u1")
    role_id = Id("r1")
    role_tree = PermissionTree()
    role_tree.add("read/users/*")

    store = TreeStore()
    store.role_ids_by_user_id[str(user_id)] = [str(role_id)]
    store.role_tree_by_role_id[str(role_id)] = role_tree

    udao = UDao([])
    rdao = RDao([])
    pdao = PDao([])
    service = AuthorizationService(udao, rdao, pdao, store)

    assert not service.user_has_access(user_id, "delete/users/123")
    assert udao.calls == 0
    assert rdao.calls == 0
    assert pdao.calls == 0


def test_role_store_loads_once():
    user_id = Id("u1")
    role_id = Id("r1")
    p = P("read/users/*")

    udao = UDao([UR(user_id=user_id, role_id=role_id)])
    rdao = RDao([RP(role_id=role_id, permission_id=p._id)])
    pdao = PDao([p])
    service = AuthorizationService(udao, rdao, pdao, TreeStore())

    assert service.user_has_access(user_id, "read/users/123")
    assert service.user_has_access(user_id, "read/users/456")
    assert udao.calls == 1
    assert rdao.calls == 1
    assert pdao.calls == 1
