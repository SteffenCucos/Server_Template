import asyncio
from unittest.mock import create_autospec

from auth.authorization_service import AuthorizationService
from auth.rbac import Permission, PermissionTree, RolePermission, TreeStore, UserRole
from auth.rbac.daos import PermDAO, RolePermDAO, UserRoleDAO
from models.base.id import Id


def _mock_daos():
    return (
        create_autospec(UserRoleDAO, instance=True),
        create_autospec(RolePermDAO, instance=True),
        create_autospec(PermDAO, instance=True),
    )


def test_role_store_no_reload_on_no_match():
    async def run_test():
        user_id = Id("u1")
        role_id = Id("r1")
        role_tree = PermissionTree()
        role_tree.add("read/users/*")

        store = TreeStore()
        store.role_ids_by_user_id[str(user_id)] = [str(role_id)]
        store.role_tree_by_role_id[str(role_id)] = role_tree

        user_role_dao, role_perm_dao, perm_dao = _mock_daos()
        service = AuthorizationService(user_role_dao, role_perm_dao, perm_dao, store)

        assert not await service.user_has_access(user_id, "delete/users/123")
        user_role_dao.list_for_user.assert_not_awaited()
        role_perm_dao.list_for_role.assert_not_awaited()
        perm_dao.get_by_id.assert_not_awaited()

    asyncio.run(run_test())


def test_role_store_loads_once():
    async def run_test():
        user_id = Id("u1")
        role_id = Id("r1")
        permission = Permission("read/users/*")

        user_role_dao, role_perm_dao, perm_dao = _mock_daos()
        user_role_dao.list_for_user.return_value = [
            UserRole(user_id=user_id, role_id=role_id),
        ]
        role_perm_dao.list_for_role.return_value = [
            RolePermission(role_id=role_id, permission_id=permission._id),
        ]
        perm_dao.get_by_id.return_value = permission

        service = AuthorizationService(
            user_role_dao,
            role_perm_dao,
            perm_dao,
            TreeStore(),
        )

        assert await service.user_has_access(user_id, "read/users/123")
        assert await service.user_has_access(user_id, "read/users/456")

        user_role_dao.list_for_user.assert_awaited_once_with(user_id)
        role_perm_dao.list_for_role.assert_awaited_once_with(role_id)
        perm_dao.get_by_id.assert_awaited_once_with(permission._id)

    asyncio.run(run_test())
