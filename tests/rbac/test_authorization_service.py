from unittest.mock import create_autospec

from auth.authorization_service import AuthorizationService
from auth.rbac import Permission, RolePermission, TreeStore, UserRole
from auth.rbac.daos import PermDAO, RolePermDAO, UserRoleDAO
from models.base.id import Id


def test_user_has_access_through_role_permission():
    user_id = Id("user-1")
    role_id = Id("admin")
    perm = Permission("read/users/.+")

    user_role_dao = create_autospec(UserRoleDAO, instance=True)
    role_perm_dao = create_autospec(RolePermDAO, instance=True)
    perm_dao = create_autospec(PermDAO, instance=True)

    user_role_dao.list_for_user.return_value = [
        UserRole(user_id=user_id, role_id=role_id),
    ]
    role_perm_dao.list_for_role.return_value = [
        RolePermission(role_id=role_id, permission_id=perm._id),
    ]
    perm_dao.get_by_id.return_value = perm

    service = AuthorizationService(
        user_role_dao,
        role_perm_dao,
        perm_dao,
        TreeStore(),
    )

    assert service.user_has_access(user_id, "read/users/123")
    assert not service.user_has_access(user_id, "delete/users/123")

    user_role_dao.list_for_user.assert_called_once_with(user_id)
    role_perm_dao.list_for_role.assert_called_once_with(role_id)
    perm_dao.get_by_id.assert_called_once_with(perm._id)
