

from typing import TypeVar

from models.base.entity import IdEntity
from models.base.id import Id

from db.base_dao import BaseDAO

T = TypeVar('T', IdEntity, None)


class EntityDAO(BaseDAO[T]):

    def find_one_by_id(self, id: Id) -> T | None:
        return self.find_one_by_condition({"_id": id})

    def save(self, entity: T) -> Id:
        EntityDAO.prep_for_save(entity)
        return super().save(entity)

    def save_many(self, lst: list[T]) -> list[Id]:
        for entity in lst:
            EntityDAO.prep_for_save(entity)
        return super().save_many(lst)

    def update(self, entity: T):
        EntityDAO.prep_for_save(entity)
        super().update(entity)

    def update_many(self, lst: list[T]):
        for entity in lst:
            EntityDAO.prep_for_save(entity)
        return super().update_many(lst)

    def delete_by_id(self, id: Id):
        self.collection.delete_one({"_id": id})

    @staticmethod
    def prep_for_save(entity: T):
        EntityDAO.validate_has_id(entity)
        if not hasattr(object, "_created_date"):
            entity.set_created_date()
        entity.set_updated_date()

    @staticmethod
    def validate_has_id(entity: T):
        if not hasattr(entity, "_id"):
            raise Exception("object must have _id field")
