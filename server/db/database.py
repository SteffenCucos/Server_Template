"""Backend-neutral database facade for DAO-style persistence.

The Database class exposes primitive record operations used by BaseDAO while
keeping pymongo/psycopg details inside private backend adapters.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .config import DatabaseBackend, DatabaseSettings

Record = dict[str, Any]
IdValue = str


@dataclass(frozen=True)
class DatabaseUpdate:
    """Backend-neutral update operation.

    This replaces driver-specific update objects such as pymongo.UpdateOne in
    DAO code. Concrete backends translate it to their native update operation.
    """

    entity_id: IdValue
    values: Record


@runtime_checkable
class DatabaseAdapter(Protocol):
    """Primitive database operations required by BaseDAO."""

    def save(self, record: Mapping[str, Any]) -> IdValue:
        """Persist one record and return its public id."""
        ...

    def save_many(self, records: Sequence[Mapping[str, Any]]) -> list[IdValue]:
        """Persist many records and return their public ids."""
        ...

    def update(self, update: DatabaseUpdate) -> None:
        """Apply one update."""
        ...

    def update_many(self, updates: Sequence[DatabaseUpdate]) -> None:
        """Apply many updates."""
        ...

    def find_all(self) -> list[Record]:
        """Return every record from the backing resource."""
        ...

    def find_one(self, condition: Mapping[str, Any]) -> Record | None:
        """Return one matching record, or None."""
        ...

    def close(self) -> None:
        """Release backend resources."""
        ...


class Database:
    """Generic database facade that maps to Mongo or Postgres.

    Public methods use only backend-neutral records, ids, and DatabaseUpdate
    objects. Mongo collections, Postgres connections/cursors, SQL objects, and
    bulk operation classes are not exposed to DAOs or endpoint code.
    """

    def __init__(
        self,
        *,
        settings: DatabaseSettings | None = None,
        resource_name: str,
        id_field: str = "_id",
    ) -> None:
        self.settings = settings or DatabaseSettings.from_env()
        self.resource_name = resource_name
        self.id_field = id_field
        self._adapter = self._create_adapter()

    def save(self, record: Mapping[str, Any]) -> IdValue:
        return self._adapter.save(record)

    def save_many(self, records: Sequence[Mapping[str, Any]]) -> list[IdValue]:
        return self._adapter.save_many(records)

    def update(self, update: DatabaseUpdate) -> None:
        self._adapter.update(update)

    def update_many(self, updates: Sequence[DatabaseUpdate]) -> None:
        self._adapter.update_many(updates)

    def find_all(self) -> list[Record]:
        return self._adapter.find_all()

    def find_one(self, condition: Mapping[str, Any]) -> Record | None:
        return self._adapter.find_one(condition)

    def close(self) -> None:
        self._adapter.close()

    def _create_adapter(self) -> DatabaseAdapter:
        if self.settings.backend == DatabaseBackend.MONGO:
            return MongoDatabaseAdapter(
                uri=self.settings.uri,
                database=self.settings.database,
                collection=self.resource_name,
                id_field=self.id_field,
            )

        if self.settings.backend == DatabaseBackend.POSTGRES:
            return PostgresJsonDatabaseAdapter(
                uri=self.settings.uri,
                table=self.resource_name,
                id_field=self.id_field,
            )

        raise ValueError(f"unsupported database backend: {self.settings.backend}")


class MongoDatabaseAdapter:
    """Mongo implementation of the generic Database facade."""

    def __init__(self, *, uri: str, database: str, collection: str, id_field: str = "_id") -> None:
        from pymongo import MongoClient

        self._client = MongoClient(uri)
        self._collection = self._client[database][collection]
        self._id_field = id_field

    def save(self, record: Mapping[str, Any]) -> IdValue:
        backend_record = self._to_backend_record(record)
        result = self._collection.insert_one(backend_record)
        return str(result.inserted_id)

    def save_many(self, records: Sequence[Mapping[str, Any]]) -> list[IdValue]:
        backend_records = [self._to_backend_record(record) for record in records]
        if not backend_records:
            return []
        result = self._collection.insert_many(backend_records)
        return [str(inserted_id) for inserted_id in result.inserted_ids]

    def update(self, update: DatabaseUpdate) -> None:
        self._collection.update_one(
            {"_id": update.entity_id},
            {"$set": self._to_backend_patch(update.values)},
        )

    def update_many(self, updates: Sequence[DatabaseUpdate]) -> None:
        from pymongo import UpdateOne

        operations = [
            UpdateOne({"_id": update.entity_id}, {"$set": self._to_backend_patch(update.values)})
            for update in updates
        ]
        if operations:
            self._collection.bulk_write(operations)

    def find_all(self) -> list[Record]:
        return [self._from_backend_record(record) for record in self._collection.find({})]

    def find_one(self, condition: Mapping[str, Any]) -> Record | None:
        record = self._collection.find_one(self._to_backend_condition(condition))
        if record is None:
            return None
        return self._from_backend_record(record)

    def close(self) -> None:
        self._client.close()

    def _to_backend_record(self, record: Mapping[str, Any]) -> Record:
        backend_record = dict(record)
        entity_id = backend_record.pop(self._id_field, None)
        if entity_id is None:
            entity_id = backend_record.get("_id") or str(uuid.uuid4())
        backend_record["_id"] = str(entity_id)
        return backend_record

    def _to_backend_patch(self, values: Mapping[str, Any]) -> Record:
        patch = dict(values)
        patch.pop("_id", None)
        patch.pop(self._id_field, None)
        return patch

    def _to_backend_condition(self, condition: Mapping[str, Any]) -> Record:
        query = dict(condition)
        if self._id_field != "_id" and self._id_field in query:
            query["_id"] = str(query.pop(self._id_field))
        if "_id" in query:
            query["_id"] = str(query["_id"])
        return query

    def _from_backend_record(self, record: Mapping[str, Any]) -> Record:
        public_record = dict(record)
        if "_id" in public_record:
            public_record[self._id_field] = str(public_record.pop("_id"))
        return public_record


class PostgresJsonDatabaseAdapter:
    """Postgres implementation of the generic Database facade.

    Records are stored as `id TEXT PRIMARY KEY` plus a JSONB payload so BaseDAO
    can use the same API for SQL and NoSQL. Service-specific DAOs can later swap
    this implementation for normalized relational tables behind the same facade.
    """

    def __init__(
        self,
        *,
        uri: str,
        table: str,
        id_field: str = "_id",
        data_column: str = "data",
        ensure_table: bool = True,
    ) -> None:
        import psycopg

        self._connection = psycopg.connect(uri)
        self._table = table
        self._id_field = id_field
        self._data_column = data_column

        if ensure_table:
            self._ensure_table()

    def save(self, record: Mapping[str, Any]) -> IdValue:
        from psycopg import sql
        from psycopg.types.json import Jsonb

        entity_id, payload = self._split_record(record)
        query = sql.SQL(
            "INSERT INTO {table} (id, {data_column}) "
            "VALUES (%s, %s) "
            "RETURNING id"
        ).format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query, (entity_id, Jsonb(payload)))
            saved_id = cursor.fetchone()[0]
        self._connection.commit()
        return str(saved_id)

    def save_many(self, records: Sequence[Mapping[str, Any]]) -> list[IdValue]:
        return [self.save(record) for record in records]

    def update(self, update: DatabaseUpdate) -> None:
        from psycopg import sql
        from psycopg.types.json import Jsonb

        patch = self._payload_from_values(update.values)
        existing = self._fetch_payload(update.entity_id)
        if existing is None:
            return

        updated = dict(existing)
        updated.update(patch)
        query = sql.SQL(
            "UPDATE {table} "
            "SET {data_column} = %s "
            "WHERE id = %s"
        ).format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query, (Jsonb(updated), update.entity_id))
        self._connection.commit()

    def update_many(self, updates: Sequence[DatabaseUpdate]) -> None:
        for update in updates:
            self.update(update)

    def find_all(self) -> list[Record]:
        from psycopg import sql

        query = sql.SQL("SELECT id, {data_column} FROM {table} ORDER BY id ASC").format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return [self._row_to_record(row) for row in rows]

    def find_one(self, condition: Mapping[str, Any]) -> Record | None:
        where_clause, params = self._build_where_clause(condition)
        if where_clause is None:
            rows = self.find_all()
            return rows[0] if rows else None

        from psycopg import sql

        query = sql.SQL("SELECT id, {data_column} FROM {table} WHERE ").format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        ) + where_clause + sql.SQL(" LIMIT 1")
        with self._connection.cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

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

    def _split_record(self, record: Mapping[str, Any]) -> tuple[IdValue, Record]:
        public_record = dict(record)
        entity_id = public_record.pop(self._id_field, None)
        if entity_id is None:
            entity_id = public_record.pop("_id", None) or str(uuid.uuid4())
        return str(entity_id), public_record

    def _payload_from_values(self, values: Mapping[str, Any]) -> Record:
        payload = dict(values)
        payload.pop(self._id_field, None)
        payload.pop("_id", None)
        return payload

    def _fetch_payload(self, entity_id: IdValue) -> Record | None:
        from psycopg import sql

        query = sql.SQL("SELECT {data_column} FROM {table} WHERE id = %s").format(
            table=sql.Identifier(self._table),
            data_column=sql.Identifier(self._data_column),
        )
        with self._connection.cursor() as cursor:
            cursor.execute(query, (entity_id,))
            row = cursor.fetchone()
        if row is None:
            return None
        return dict(row[0] or {})

    def _build_where_clause(self, condition: Mapping[str, Any]):
        from psycopg import sql

        if not condition:
            return None, ()

        clauses = []
        params: list[Any] = []
        for field, value in condition.items():
            if field in {self._id_field, "_id", "id"}:
                clauses.append(sql.SQL("id = %s"))
                params.append(str(value))
            else:
                clauses.append(
                    sql.SQL("{data_column}->>{field} = %s").format(
                        data_column=sql.Identifier(self._data_column),
                        field=sql.Literal(str(field)),
                    )
                )
                params.append(str(value))

        where_clause = clauses[0]
        for clause in clauses[1:]:
            where_clause = where_clause + sql.SQL(" AND ") + clause
        return where_clause, tuple(params)

    def _row_to_record(self, row: tuple[str, Mapping[str, Any]]) -> Record:
        entity_id, payload = row
        record = dict(payload or {})
        record[self._id_field] = str(entity_id)
        return record
