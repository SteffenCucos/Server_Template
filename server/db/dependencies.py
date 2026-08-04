"""FastAPI dependency providers for repository and DAO injection."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Annotated, TypeVar

from auth.rbac import Permission as PermModel
from auth.rbac import Role, RolePermission, UserRole
from auth.session.session import Session
from fastapi import Depends
from users.user import User

from auth.session.session_dao import SessionDAO

from .config import DatabaseSettings
from .repository.factory import create_repository
from .pserialize_entity_serializer import PSerializeEntitySerializer
from .repository import EntitySerializer, Repository
from users.user_dao import UserDAO

if TYPE_CHECKING:
    from auth.rbac.daos import PermDAO, RoleDAO, RolePermDAO, UserRoleDAO

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

