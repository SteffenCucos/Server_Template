"""Postgres implementation of the backend-neutral repository contract.

This starter implementation stores each entity as an id plus JSONB payload. That
keeps the repository contract backend-neutral while still allowing teams to move
to first-class relational tables later behind the same Repository protocol.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic

from ..connection import create_postgres_connection
from ..repository import EntityIdRequiredError, EntitySerializer, EntityT


class PostgresRepository(Generic[EntityT]):
    """Repository implementation backed by PostgreSQL.

    Public constructor arguments are plain strings and serializers. psycopg
    connection/cursor/sql objects are created and kept internally.
    """

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
        self._connection = create_postgres_connection(uri)
        self._table = table
        self._serializer = serializer
        self._id_field = id_field
        self._data_column = data_column

        if ensure_table:
            self._ensure_table()

    def create(self, entity: EntityT) -> EntityT:
        from psycopg import sql
        from psycopg.types.json import Jsonb

        record = dict(self._serializer.to_record(entity))
        entity_id = self._extract_id(record)
        payload = self._payload_without_id(record)

        query = sql.SQL(
            "INSERT INTO {table} (id, {data_column}) "
            "VALUES (%s, %s) "
            "RETURNING id, {data_column}"
        ).format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query, (entity_id, Jsonb(payload)))
            row = cursor.fetchone()
        self._connection.commit()
        return self._row_to_entity(row)

    def get_by_id(self, entity_id: str) -> EntityT | None:
        row = self._fetch_row(entity_id)
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
        from psycopg import sql

        query = sql.SQL(
            "SELECT id, {data_column} "
            "FROM {table} "
            "ORDER BY id ASC "
            "LIMIT %s OFFSET %s"
        ).format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
        return [self._row_to_entity(row) for row in rows]

    def update(self, entity_id: str, changes: Mapping[str, Any]) -> EntityT | None:
        from psycopg import sql
        from psycopg.types.json import Jsonb

        existing = self._fetch_row(entity_id)
        if existing is None:
            return None

        _, current_payload = existing
        updated_payload = dict(current_payload or {})
        updated_payload.update({key: value for key, value in changes.items() if key != self._id_field})

        query = sql.SQL(
            "UPDATE {table} "
            "SET {data_column} = %s "
            "WHERE id = %s "
            "RETURNING id, {data_column}"
        ).format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query, (Jsonb(updated_payload), entity_id))
            row = cursor.fetchone()
        self._connection.commit()
        return self._row_to_entity(row)

    def delete(self, entity_id: str) -> bool:
        from psycopg import sql

        query = sql.SQL("DELETE FROM {table} WHERE id = %s").format(
            table=sql.Identifier(self._table),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query, (entity_id,))
            deleted_count = cursor.rowcount
        self._connection.commit()
        return deleted_count > 0

    def close(self) -> None:
        self._connection.close()

    def _ensure_table(self) -> None:
        from psycopg import sql

        query = sql.SQL(
            "CREATE TABLE IF NOT EXISTS {table} ("
            "id TEXT PRIMARY KEY, "
            "{data_column} JSONB NOT NULL DEFAULT '{{}}'::jsonb"
            ")"
        ).format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query)
        self._connection.commit()

    def _fetch_row(self, entity_id: str) -> tuple[str, dict[str, Any]] | None:
        from psycopg import sql

        query = sql.SQL("SELECT id, {data_column} FROM {table} WHERE id = %s").format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query, (entity_id,))
            return cursor.fetchone()

    def _extract_id(self, record: Mapping[str, Any]) -> str:
        if self._id_field not in record:
            raise EntityIdRequiredError(f"entity record must include {self._id_field!r}")
        return str(record[self._id_field])

    def _payload_without_id(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in record.items() if key != self._id_field}

    def _row_to_entity(self, row: tuple[str, dict[str, Any]] | None) -> EntityT:
        if row is None:
            raise LookupError("expected database row, got None")

        entity_id, payload = row
        record = dict(payload or {})
        record[self._id_field] = entity_id
        return self._serializer.from_record(record)
