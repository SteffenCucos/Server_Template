"""FastAPI dependency providers for repository injection.

Endpoints can depend on typed repository aliases such as `UserRepository` and
`SessionRepository` without knowing which concrete database backend is active.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from typing import Annotated, Any, Generic, TypeVar

from auth.session.session import Session
from fastapi import Depends
from models.user.user import User

from .config import DatabaseSettings
from .factory import create_repository
from .repository import EntitySerializer, Repository
from .serializing_middleware import (
    get_application_deserializer,
    get_application_serializer,
)

EntityT = TypeVar("EntityT")
Record = dict[str, Any]


class PSerializeEntitySerializer(Generic[EntityT]):
    """EntitySerializer backed by the template's pserialize middleware."""

    def __init__(self, class_type: type[EntityT]) -> None:
        self.class_type = class_type
        self.serializer = get_application_serializer()
        self.deserializer = get_application_deserializer()

    def to_record(self, entity: EntityT) -> Record:
        return self.serializer.serialize(entity)

    def from_record(self, record: Mapping[str, Any]) -> EntityT:
        return self.deserializer.deserialize(value=dict(record), classType=self.class_type)


def get_database_settings() -> DatabaseSettings:
    """Resolve database settings for the current request."""
    return DatabaseSettings.from_env()


def repository_dependency(
    *,
    resource_name: str,
    serializer: EntitySerializer[EntityT],
    id_field: str = "_id",
) -> Callable[..., Iterator[Repository[EntityT]]]:
    """Create a FastAPI dependency for a typed repository.

    The dependency opens the concrete repository for the configured backend and
    closes it when the request finishes.
    """

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

UserRepository = Annotated[Repository[User], Depends(get_user_repository)]
SessionRepository = Annotated[Repository[Session], Depends(get_session_repository)]
