"""FastAPI dependency providers for repository and DAO injection.

Endpoints and services can depend on explicit dependency providers without
knowing which concrete database backend is active.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Annotated, TypeVar

from auth.session.session import Session
from fastapi import Depends
from models.user.user import User

from .config import DatabaseSettings
from .factory import create_repository
from .pserialize_entity_serializer import PSerializeEntitySerializer
from .repository import EntitySerializer, Repository
from .session_dao import SessionDAO
from .user_dao import UserDAO

EntityT = TypeVar("EntityT")


def get_database_settings() -> DatabaseSettings:
    """Resolve database settings for the current request."""
    return DatabaseSettings.from_env()


def repository_dependency(
    *,
    resource_name: str,
    serializer: EntitySerializer[EntityT],
    id_field: str = "_id",
) -> Callable[..., Iterator[Repository[EntityT]]]:
    """Create a FastAPI dependency for a typed repository."""

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


def get_user_dao(
    user_repository: Annotated[Repository[User], Depends(get_user_repository)],
) -> UserDAO:
    return UserDAO(user_repository)


def get_session_dao(
    session_repository: Annotated[Repository[Session], Depends(get_session_repository)],
) -> SessionDAO:
    return SessionDAO(session_repository)
