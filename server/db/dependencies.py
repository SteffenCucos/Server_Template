"""FastAPI dependency providers for repository injection.

Endpoints can depend on typed repository aliases such as `UserRepository` and
`SessionRepository` without knowing which concrete database backend is active.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from dataclasses import fields, is_dataclass
from typing import Annotated, Any, Generic, TypeVar

from auth.session.session import Session
from fastapi import Depends
from models.base.id import Id
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
        self.constructor_fields = _constructor_fields(class_type)

    def to_record(self, entity: EntityT) -> Record:
        record = self.serializer.serialize(entity)
        if hasattr(entity, "_id") and "_id" not in record:
            record["_id"] = str(getattr(entity, "_id"))
        return record

    def from_record(self, record: Mapping[str, Any]) -> EntityT:
        record_dict = dict(record)
        constructor_record = {
            key: value
            for key, value in record_dict.items()
            if key in self.constructor_fields
        }
        entity = self.deserializer.deserialize(
            value=constructor_record,
            classType=self.class_type,
        )

        for key, value in record_dict.items():
            if key == "_id":
                setattr(entity, key, Id(str(value)))
            elif key not in self.constructor_fields:
                setattr(entity, key, value)

        return entity


def _constructor_fields(class_type: type[Any]) -> set[str]:
    if not is_dataclass(class_type):
        return set()
    return {field.name for field in fields(class_type) if field.init}


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
