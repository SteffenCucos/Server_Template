from models.id import Id
from .serializing_middleware import get_application_serializer, get_application_deserializer
from pymongo import UpdateOne
from pymongo.collection import Collection
from typing import TypeVar, Generic

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

    def find_one_by_name(self, name: str) -> T:
        return self.find_one_by_condition({"name": name})

    def find_one_by_id(self, id: str) -> T:
        return self.find_one_by_condition({"_id": id})

    def find_one_by_condition(self, condition: dict) -> T:
        ret = self.collection.find_one(condition)
        if ret:
            return self.deserializer.deserialize(value=ret, classType=self.classType)
        return None

    def get_id_criteria(self, object):
        return {
            "_id": object._id
        }

    # Save all the fields from the object into mongo
    def get_update_query(self, object):
        return {
            "$set": self.serializer.serialize(object)
        }
