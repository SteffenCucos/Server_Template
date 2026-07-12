"""FastAPI dependency providers for repository and DAO injection."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Annotated, TypeVar

from auth.rbac import Permission as PermModel
from auth.rbac import Role, RolePermission, UserRole
from auth.session.session import Session
from fastapi import Depends
from models.user.user import User

from .config import DatabaseSettings
from .repository.factory import create_repository
from .pserialize_entity_serializer import PSerializeEntitySerializer
from .daos.rbac import PermDAO, RoleDAO, RolePermDAO, UserRoleDAO
from .repository import EntitySerializer, Repository
from .daos.session_dao import SessionDAO
from .daos.user_dao import UserDAO

EntityT = TypeVar("EntityT")


def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings.from_env()


def repository_dependency(
    *,
    resource_name: str,
    serializer: EntitySerializer[EntityT],
    id_field: str = "_id",
) -> Callable[..., Iterator[Repository[EntityT]]]:
    def get_repository(
        settings: DatabaseSettings = Depends(get_database_settings),
    ) -> Iterator[Repository[EntityT]]:
        repository = create_repository(
            settings=settings,
            resource_name=resource_name,
            serializer=serializer,
            id_field=id_field,
        )
        try:
            yield repository
        finally:
            repository.close()

    return get_repository


get_user_repository = repository_dependency(
    resource_name="users",
    serializer=PSerializeEntitySerializer(User),
)

get_session_repository = repository_dependency(
    resource_name="sessions",
    serializer=PSerializeEntitySerializer(Session),
)

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


def get_user_dao(
    user_repository: Annotated[Repository[User], Depends(get_user_repository)],
) -> UserDAO:
    return UserDAO(user_repository)


def get_session_dao(
    session_repository: Annotated[Repository[Session], Depends(get_session_repository)],
) -> SessionDAO:
    return SessionDAO(session_repository)


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
