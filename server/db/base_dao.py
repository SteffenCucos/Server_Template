from typing import Generic, TypeVar

from models.base.id import Id
from pymongo import UpdateOne
from pymongo.collection import Collection

from .serializing_middleware import (get_application_deserializer,
                                     get_application_serializer)

T = TypeVar('T')


class BaseDAO(Generic[T]):
    def __init__(
        self,
        collection: Collection = None,
        classType: type = None
    ):
        self.collection = collection
        self.classType = classType
        self.serializer = get_application_serializer()
        self.deserializer = get_application_deserializer()

    def save(self, object: T) -> Id:
        return self.collection.insert_one(self.serializer.serialize(object)).inserted_id

    def save_many(self, lst: list[T]) -> list[Id]:
        serialized = self.serializer.serialize(lst)
        inserted = self.collection.insert_many(serialized)
        return inserted

    def update(self, object: T):
        self.collection.update_one(self.get_id_criteria(
            object), self.get_update_query(object))

    def update_request(self, object: T) -> UpdateOne:
        return UpdateOne(self.get_id_criteria(object), self.get_update_query(object))

    def update_many(self, lst: list[T]):
        self.collection.bulk_write(
            [self.update_request(object) for object in lst])

    def find_all(self) -> list[T]:
        return self.deserializer.deserialize(value=list(self.collection.find({})), classType=list[self.classType])

    def find_one_by_condition(self, condition: dict) -> T | None:
        ret = self.collection.find_one(condition)
        if ret:
            return self.deserializer.deserialize(value=ret, classType=self.classType)
        return None

    # Save all the fields from the object into mongo
    def get_update_query(self, object):
        return {
            "$set": self.serializer.serialize(object)
        }

    def get_id_criteria(self, entity: T):
        return {
            "_id": entity._id
        }
