

from .base_dao import BaseDAO
from ..models.entity import IdEntity
from ..models.id import Id


class EntityDAO(BaseDAO):

    def save(self, entity: IdEntity) -> Id:
        EntityDAO.prep_for_save(entity)
        return super().save(entity)

    def save_many(self, lst: list[IdEntity]) -> list[Id]:
        for entity in lst:
            EntityDAO.prep_for_save(entity)
        return super().save_many(lst)

    def update(self, entity: IdEntity):
        EntityDAO.prep_for_save(entity)
        super().update(entity)

    def update_many(self, lst: list[IdEntity]):
        for entity in lst:
            EntityDAO.prep_for_save(entity)
        return super().update_many(lst)

    @staticmethod
    def prep_for_save(entity: IdEntity):
        EntityDAO.validate_has_id(entity)
        if not hasattr(object, "_created_date"):
            entity.set_created_date()
        entity.set_updated_date()

    @staticmethod
    def validate_has_id(object: object):
        if not hasattr(object, "_id"):
            raise Exception("object must have _id field")
