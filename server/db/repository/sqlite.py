"""SQLite implementation of the backend-neutral repository contract.

This implementation stores each entity as an id plus JSON payload. It is useful
for local development, lightweight services, and in-memory CI tests.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .repository import EntityIdRequiredError, EntitySerializer, EntityT, Repository

_MEMORY_SQLITE_URIS = {":memory:", "sqlite:///:memory:"}
_SHARED_MEMORY_CONNECTIONS: dict[str, sqlite3.Connection] = {}


class SQLiteRepository(Repository[EntityT]):
    """Repository implementation backed by SQLite."""

    def __init__(
        self,
        *,
        uri: str,
        table: str,
        serializer: EntitySerializer[EntityT],
        id_field: str = "id",
        data_column: str = "data",
        ensure_table: bool = True,
    ) -> None:
        self._connection, self._owns_connection = _create_sqlite_connection(uri)
        self._connection.row_factory = sqlite3.Row
        self._table = table
        self._serializer = serializer
        self._id_field = id_field
        self._data_column = data_column

        if ensure_table:
            self._ensure_table()

    def create(self, entity: EntityT) -> EntityT:
        record = dict(self._serializer.to_record(entity))
        entity_id = self._extract_id(record)
        payload = self._payload_without_id(record)

        self._connection.execute(
            f'INSERT INTO "{self._table}" (id, "{self._data_column}") VALUES (?, ?)',
            (entity_id, json.dumps(payload, default=str)),
        )
        self._connection.commit()
        return self.get_by_id(entity_id)

    def get_by_id(self, entity_id: str) -> EntityT | None:
        row = self._connection.execute(
            f'SELECT id, "{self._data_column}" FROM "{self._table}" WHERE id = ?',
            (entity_id,),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_entity(row)

    def find_one(self, condition: Mapping[str, Any]) -> EntityT | None:
        if not condition:
            entities = self.list(limit=1)
            return entities[0] if entities else None

        if len(condition) == 1:
            field, value = next(iter(condition.items()))
            if field in {self._id_field, "_id", "id"}:
                return self.get_by_id(str(value))

        for entity in self.list(limit=10_000):
            record = self._serializer.to_record(entity)
            if all(str(record.get(field)) == str(value) for field, value in condition.items()):
                return entity
        return None

    def list(self, *, limit: int = 100, offset: int = 0) -> list[EntityT]:
        rows = self._connection.execute(
            f'SELECT id, "{self._data_column}" FROM "{self._table}" ORDER BY id ASC LIMIT ? OFFSET ?',
            (limit, offset),
        ).fetchall()
        return [self._row_to_entity(row) for row in rows]

    def update(self, entity_id: str, changes: Mapping[str, Any]) -> EntityT | None:
        current = self.get_by_id(entity_id)
        if current is None:
            return None

        record = self._serializer.to_record(current)
        record.update({key: value for key, value in changes.items() if key != self._id_field})
        payload = self._payload_without_id(record)
        self._connection.execute(
            f'UPDATE "{self._table}" SET "{self._data_column}" = ? WHERE id = ?',
            (json.dumps(payload, default=str), entity_id),
        )
        self._connection.commit()
        return self.get_by_id(entity_id)

    def delete(self, entity_id: str) -> bool:
        cursor = self._connection.execute(
            f'DELETE FROM "{self._table}" WHERE id = ?',
            (entity_id,),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        if self._owns_connection:
            self._connection.close()

    def _ensure_table(self) -> None:
        self._connection.execute(
            f'CREATE TABLE IF NOT EXISTS "{self._table}" ('
            f'id TEXT PRIMARY KEY, "{self._data_column}" TEXT NOT NULL DEFAULT "{{}}")'
        )
        self._connection.commit()

    def _extract_id(self, record: Mapping[str, Any]) -> str:
        if self._id_field not in record:
            raise EntityIdRequiredError(f"entity record must include {self._id_field!r}")
        return str(record[self._id_field])

    def _payload_without_id(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in record.items() if key != self._id_field}

    def _row_to_entity(self, row: sqlite3.Row) -> EntityT:
        payload = json.loads(row[self._data_column] or "{}")
        record = dict(payload)
        record[self._id_field] = row["id"]
        return self._serializer.from_record(record)


def _create_sqlite_connection(uri: str) -> tuple[sqlite3.Connection, bool]:
    if uri in _MEMORY_SQLITE_URIS:
        if uri not in _SHARED_MEMORY_CONNECTIONS:
            _SHARED_MEMORY_CONNECTIONS[uri] = sqlite3.connect(":memory:", check_same_thread=False)
        return _SHARED_MEMORY_CONNECTIONS[uri], False

    return sqlite3.connect(_sqlite_path_from_uri(uri), check_same_thread=False), True


def _sqlite_path_from_uri(uri: str) -> str:
    parsed = urlparse(uri)
    if parsed.scheme != "sqlite":
        return uri

    path = parsed.path
    if path.startswith("/") and not path.startswith("//"):
        path = path[1:]

    db_path = Path(path)
    if db_path.parent != Path(""):
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path)
