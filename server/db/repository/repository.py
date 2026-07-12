"""Backend-neutral repository contracts.

The Repository is the application interface to the underlying database. It
exposes only application concepts and primitive Python values, while concrete
backend implementations own all driver-specific concerns.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Generic, TypeVar

EntityT = TypeVar("EntityT")
Record = dict[str, Any]


class EntitySerializer(ABC, Generic[EntityT]):
    """Convert between application entities and plain persistence records.

    Implement this per model when your entity is a dataclass, Pydantic model, or
    other domain object. The returned record must contain only JSON-like Python
    values if it is going to be stored by both Mongo and Postgres backends.
    """

    @abstractmethod
    def to_record(self, entity: EntityT) -> Record:
        """Convert an application entity to a backend-neutral record."""
        raise NotImplementedError

    @abstractmethod
    def from_record(self, record: Mapping[str, Any]) -> EntityT:
        """Convert a backend-neutral record to an application entity."""
        raise NotImplementedError


class MappingSerializer(EntitySerializer[Record]):
    """Pass-through serializer for apps that use dict records directly."""

    def to_record(self, entity: Record) -> Record:
        return dict(entity)

    def from_record(self, record: Mapping[str, Any]) -> Record:
        return dict(record)


class Repository(ABC, Generic[EntityT]):
    """Minimal CRUD contract shared by every storage backend.

    This abstraction intentionally avoids pymongo, psycopg, SQLAlchemy, cursor,
    collection, query-builder, or transaction/session types. Backend-specific
    implementations can use those internally, but endpoint/service code should
    only depend on this base interface through DAOs.
    """

    @abstractmethod
    def create(self, entity: EntityT) -> EntityT:
        """Persist a new entity and return the stored entity."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: str) -> EntityT | None:
        """Return one entity by public id, or None when not found."""
        raise NotImplementedError

    @abstractmethod
    def find_one(self, condition: Mapping[str, Any]) -> EntityT | None:
        """Return one entity matching a primitive equality condition."""
        raise NotImplementedError

    @abstractmethod
    def list(self, *, limit: int = 100, offset: int = 0) -> list[EntityT]:
        """Return entities in deterministic backend order."""
        raise NotImplementedError

    @abstractmethod
    def update(self, entity_id: str, changes: Mapping[str, Any]) -> EntityT | None:
        """Patch primitive field values and return the updated entity."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete one entity by public id and return whether anything changed."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Release backend resources held by this repository."""
        raise NotImplementedError


class RepositoryError(RuntimeError):
    """Base exception for repository failures."""


class EntityIdRequiredError(RepositoryError):
    """Raised when an entity cannot be persisted because it has no id field."""
