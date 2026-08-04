from __future__ import annotations

from typing import Annotated

from auth.rbac import Permission as PermModel
from auth.rbac import Role, RolePermission, UserRole
from fastapi import Depends

from db.dependencies import repository_dependency
from db.pserialize_entity_serializer import PSerializeEntitySerializer
from db.repository import Repository

from .daos import PermDAO, RoleDAO, RolePermDAO, UserRoleDAO

get_perm_repository = repository_dependency(
    resource_name="perms",
    serializer=PSerializeEntitySerializer(PermModel),
)

get_role_repository = repository_dependency(
    resource_name="roles",
    serializer=PSerializeEntitySerializer(Role),
)

get_user_role_repository = repository_dependency(
    resource_name="user_roles",
    serializer=PSerializeEntitySerializer(UserRole),
)

get_role_perm_repository = repository_dependency(
    resource_name="role_perms",
    serializer=PSerializeEntitySerializer(RolePermission),
)


def get_perm_dao(
    repository: Annotated[Repository[PermModel], Depends(get_perm_repository)],
) -> PermDAO:
    return PermDAO(repository)


def get_role_dao(
    repository: Annotated[Repository[Role], Depends(get_role_repository)],
) -> RoleDAO:
    return RoleDAO(repository)


def get_user_role_dao(
    repository: Annotated[Repository[UserRole], Depends(get_user_role_repository)],
) -> UserRoleDAO:
    return UserRoleDAO(repository)


def get_role_perm_dao(
    repository: Annotated[Repository[RolePermission], Depends(get_role_perm_repository)],
) -> RolePermDAO:
    return RolePermDAO(repository)
