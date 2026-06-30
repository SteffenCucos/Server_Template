"""Backend-neutral database facade for DAO-style persistence.

The Database class exposes primitive record operations used by BaseDAO while
reusing the concrete MongoRepository/PostgresRepository implementations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .config import DatabaseSettings
from .factory import create_repository
from .repository import MappingSerializer, Repository

Record = dict[str, Any]
IdValue = str


@dataclass(frozen=True)
class DatabaseUpdate:
    """Backend-neutral update operation.

    This replaces driver-specific update objects such as pymongo.UpdateOne in
    DAO code. Concrete repositories translate it to their native update logic.
    """

    entity_id: IdValue
    values: Record


class Database:
    """Generic database facade that maps to Mongo or Postgres repositories.

    Public methods use only backend-neutral records, ids, and DatabaseUpdate
    objects. Mongo collections, Postgres connections/cursors, SQL objects, and
    bulk operation classes remain inside the concrete repository classes.
    """

    def __init__(
        self,
        *,
        settings: DatabaseSettings | None = None,
        resource_name: str,
        id_field: str = "_id",
        repository: Repository[Record] | None = None,
    ) -> None:
        self.settings = settings or DatabaseSettings.from_env()
        self.resource_name = resource_name
        self.id_field = id_field
        self.repository = repository or create_repository(
            settings=self.settings,
            resource_name=resource_name,
            serializer=MappingSerializer(),
            id_field=id_field,
        )

    def save(self, record: Mapping[str, Any]) -> IdValue:
        saved = self.repository.create(dict(record))
        return self._get_record_id(saved)

    def save_many(self, records: Sequence[Mapping[str, Any]]) -> list[IdValue]:
        return [self.save(record) for record in records]

    def update(self, update: DatabaseUpdate) -> None:
        self.repository.update(update.entity_id, update.values)

    def update_many(self, updates: Sequence[DatabaseUpdate]) -> None:
        for update in updates:
            self.update(update)

    def find_all(self) -> list[Record]:
        return self.repository.list(limit=10_000)

    def find_one(self, condition: Mapping[str, Any]) -> Record | None:
        return self.repository.find_one(condition)

    def close(self) -> None:
        self.repository.close()

    def _get_record_id(self, record: Mapping[str, Any]) -> IdValue:
        value = record.get(self.id_field) or record.get("_id") or record.get("id")
        if value is None:
            raise ValueError(f"saved record does not contain id field {self.id_field!r}")
        return str(value)
