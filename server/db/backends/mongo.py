"""Mongo implementation of the backend-neutral repository contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic

from ..repository import EntityIdRequiredError, EntitySerializer, EntityT

MEMORY_MONGO_URIS = {"memory://", "mongo://memory", "mongodb://memory", "mongodb://in-memory"}
_SHARED_MEMORY_CLIENTS: dict[str, object] = {}


class MongoRepository(Generic[EntityT]):
    """Repository implementation backed by MongoDB.

    Public constructor arguments are plain strings and serializers. pymongo
    collection/client objects are created and kept internally.
    """

    def __init__(
        self,
        *,
        uri: str,
        database: str,
        collection: str,
        serializer: EntitySerializer[EntityT],
        id_field: str = "id",
    ) -> None:
        self._client, self._owns_client = _create_mongo_client(uri)
        self._collection = self._client[database][collection]
        self._serializer = serializer
        self._id_field = id_field

    def create(self, entity: EntityT) -> EntityT:
        record = self._to_backend_record(self._serializer.to_record(entity))
        self._collection.insert_one(record)
        return self._from_backend_record(record)

    def get_by_id(self, entity_id: str) -> EntityT | None:
        record = self._collection.find_one({"_id": entity_id})
        if record is None:
            return None
        return self._from_backend_record(record)

    def find_one(self, condition: Mapping[str, Any]) -> EntityT | None:
        record = self._collection.find_one(self._to_backend_condition(condition))
        if record is None:
            return None
        return self._from_backend_record(record)

    def list(self, *, limit: int = 100, offset: int = 0) -> list[EntityT]:
        cursor = self._collection.find({}).sort("_id", 1).skip(offset).limit(limit)
        return [self._from_backend_record(record) for record in cursor]

    def update(self, entity_id: str, changes: Mapping[str, Any]) -> EntityT | None:
        from pymongo import ReturnDocument

        update_record = self._to_backend_patch(changes)
        if not update_record:
            return self.get_by_id(entity_id)

        record = self._collection.find_one_and_update(
            {"_id": entity_id},
            {"$set": update_record},
            return_document=ReturnDocument.AFTER,
        )
        if record is None:
            return None
        return self._from_backend_record(record)

    def delete(self, entity_id: str) -> bool:
        result = self._collection.delete_one({"_id": entity_id})
        return result.deleted_count > 0

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _to_backend_record(self, record: Mapping[str, Any]) -> dict[str, Any]:
        backend_record = dict(record)
        if "_id" in backend_record:
            backend_record["_id"] = str(backend_record["_id"])
            return backend_record

        if self._id_field not in backend_record:
            raise EntityIdRequiredError(f"entity record must include {self._id_field!r}")

        backend_record["_id"] = str(backend_record.pop(self._id_field))
        return backend_record

    def _to_backend_patch(self, changes: Mapping[str, Any]) -> dict[str, Any]:
        patch = dict(changes)
        if self._id_field in patch:
            patch["_id"] = str(patch.pop(self._id_field))
        if "_id" in patch:
            patch.pop("_id")
        return patch

    def _to_backend_condition(self, condition: Mapping[str, Any]) -> dict[str, Any]:
        query = dict(condition)
        if self._id_field in query:
            query["_id"] = str(query.pop(self._id_field))
        if "_id" in query:
            query["_id"] = str(query["_id"])
        return query

    def _from_backend_record(self, record: Mapping[str, Any]) -> EntityT:
        public_record = dict(record)
        if "_id" in public_record:
            public_record[self._id_field] = str(public_record.pop("_id"))
        return self._serializer.from_record(public_record)


def _create_mongo_client(uri: str):
    if uri in MEMORY_MONGO_URIS:
        from pymongo_inmemory import MongoClient

        if uri not in _SHARED_MEMORY_CLIENTS:
            _SHARED_MEMORY_CLIENTS[uri] = MongoClient()
        return _SHARED_MEMORY_CLIENTS[uri], False

    from pymongo import MongoClient

    return MongoClient(uri), True
