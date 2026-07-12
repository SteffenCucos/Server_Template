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
    """Repository-facing DAO for DB-backed entities.

    DAOs route persistence requests to the backend-neutral Repository contract.
    They also own database-adjacent concerns that are not generic enough for the
    Repository interface, such as entity lifecycle fields like _created_date and
    _updated_date. Business rules should stay in services instead of DAOs.
    """

    def __init__(self, repository: Repository[TEntity]):
        self.repository = repository
        self.serializer = get_application_serializer()

    def create(self, entity: TEntity) -> TEntity:
        self.prep_for_save(entity)
        return self.repository.create(entity)

    def save(self, entity: TEntity) -> Id:
        return self.create(entity)._id

    def save_many(self, entities: list[TEntity]) -> list[Id]:
        return [self.save(entity) for entity in entities]

    def get_by_id(self, entity_id: Id | str) -> TEntity | None:
        return self.repository.get_by_id(str(entity_id))

    def find_one_by_id(self, entity_id: Id | str) -> TEntity | None:
        return self.get_by_id(entity_id)

    def find_one(self, condition: Mapping[str, Any]) -> TEntity | None:
        return self.repository.find_one(condition)

    def list(self, *, limit: int = 10_000, offset: int = 0) -> list[TEntity]:
        return self.repository.list(limit=limit, offset=offset)

    def find_all(self) -> list[TEntity]:
        return self.list()

    def update(self, entity_id: Id | str, changes: Mapping[str, Any]) -> TEntity | None:
        update_record = dict(changes)
        update_record.setdefault("_updated_date", Datetime.now().isoformat())
        return self.repository.update(str(entity_id), update_record)

    def update_entity(self, entity: TEntity) -> TEntity | None:
        self.prep_for_save(entity)
        update_record = self.serializer.serialize(entity)
        update_record.pop("_id", None)
        return self.repository.update(str(entity._id), update_record)

    def update_many(self, entities: list[TEntity]) -> list[TEntity | None]:
        return [self.update_entity(entity) for entity in entities]

    def delete(self, entity_id: Id | str) -> bool:
        return self.repository.delete(str(entity_id))

    def delete_by_id(self, entity_id: Id | str) -> bool:
        return self.delete(entity_id)

    def close(self) -> None:
        self.repository.close()

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
