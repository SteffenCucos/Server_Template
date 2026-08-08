from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime as Datetime
from typing import Any, Generic, TypeVar

from models.base.entity import IdEntity
from models.base.id import Id

from db.repository import Repository
from db.serializing_middleware import get_application_serializer

TEntity = TypeVar("TEntity", bound=IdEntity)


class EntityDAO(Generic[TEntity]):
    """Repository-facing DAO for DB-backed entities."""

    def __init__(self, repository: Repository[TEntity]):
        self.repository = repository
        self.serializer = get_application_serializer()

    async def create(self, entity: TEntity) -> TEntity:
        self.prep_for_save(entity)
        return await self.repository.create(entity)

    async def save(self, entity: TEntity) -> Id:
        return (await self.create(entity))._id

    async def save_many(self, entities: list[TEntity]) -> list[Id]:
        return [await self.save(entity) for entity in entities]

    async def get_by_id(self, entity_id: Id | str) -> TEntity | None:
        return await self.repository.get_by_id(str(entity_id))

    async def find_one_by_id(self, entity_id: Id | str) -> TEntity | None:
        return await self.get_by_id(entity_id)

    async def find_one(self, condition: Mapping[str, Any]) -> TEntity | None:
        return await self.repository.find_one(condition)

    async def list(self, *, limit: int = -1, offset: int = 0) -> list[TEntity]:
        return await self.repository.list(limit=limit, offset=offset)

    async def find_all(self) -> list[TEntity]:
        return await self.list()

    async def update(
        self,
        entity_id: Id | str,
        changes: Mapping[str, Any],
    ) -> TEntity | None:
        update_record = dict(changes)
        update_record.setdefault("_updated_date", Datetime.now().isoformat())
        return await self.repository.update(str(entity_id), update_record)

    async def update_entity(self, entity: TEntity) -> TEntity | None:
        self.prep_for_save(entity)
        update_record = self.serializer.serialize(entity)
        update_record.pop("_id", None)
        return await self.repository.update(str(entity._id), update_record)

    async def update_many(self, entities: list[TEntity]) -> list[TEntity | None]:
        return [await self.update_entity(entity) for entity in entities]

    async def delete(self, entity_id: Id | str) -> bool:
        return await self.repository.delete(str(entity_id))

    async def delete_by_id(self, entity_id: Id | str) -> bool:
        return await self.delete(entity_id)

    async def close(self) -> None:
        await self.repository.close()

    @staticmethod
    def prep_for_save(entity: TEntity) -> None:
        EntityDAO.validate_has_id(entity)
        if not hasattr(entity, "_created_date"):
            entity.set_created_date()
        entity.set_updated_date()

    @staticmethod
    def validate_has_id(entity: TEntity) -> None:
        if not hasattr(entity, "_id"):
            raise ValueError("Entity must have _id")
