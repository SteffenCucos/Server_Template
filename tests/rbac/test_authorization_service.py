from auth.rbac import Permission, RolePermission, UserRole
from models.base.id import Id
from service.authorization_service import AuthorizationService


class FakeUserRoleDAO:
    def __init__(self, user_roles: list[UserRole]):
        self.user_roles = user_roles

    def list_for_user(self, user_id: Id | str) -> list[UserRole]:
        return [item for item in self.user_roles if str(item.user_id) == str(user_id)]


class FakeRolePermDAO:
    def __init__(self, role_perms: list[RolePermission]):
        self.role_perms = role_perms

    def list_for_role(self, role_id: Id | str) -> list[RolePermission]:
        return [item for item in self.role_perms if str(item.role_id) == str(role_id)]


class FakePermDAO:
    def __init__(self, perms: list[Permission]):
        self.perms = {str(perm._id): perm for perm in perms}

    def get_by_id(self, perm_id: Id | str) -> Permission | None:
        return self.perms.get(str(perm_id))


def test_user_has_access_through_role_permission():
    user_id = Id("user-1")
    role_id = Id("admin")
    perm = Permission("read/users/.+")

    service = AuthorizationService(
        FakeUserRoleDAO([UserRole(user_id=user_id, role_id=role_id)]),
        FakeRolePermDAO([RolePermission(role_id=role_id, permission_id=perm._id)]),
        FakePermDAO([perm]),
    )

    assert service.user_has_access(user_id, "read/users/123")
    assert not service.user_has_access(user_id, "delete/users/123")
