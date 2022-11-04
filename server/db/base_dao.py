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
        self.prep_for_save(object)
        return self.collection.insert_one(self.serializer.serialize(object)).inserted_id

    def save_many(self, lst: list[T]) -> list[Id]:
        for object in lst:
            self.prep_for_save(object)
        serialized = self.serializer.serialize(lst)
        inserted = self.collection.insert_many(serialized)
        return inserted

    def update(self, object: T):
        self.prep_for_save(object)
        self.collection.update_one(self.get_id_criteria(
            object), self.get_update_query(object))

    def update_request(self, object: T) -> UpdateOne:
        return UpdateOne(self.get_id_criteria(object), self.get_update_query(object))

    def update_many(self, lst: list[T]):
        for object in lst:
            self.prep_for_save(object)

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

    def prep_for_save(self, object: object):
        self.validate_has_id(object)
        if not hasattr(object, "_created_date"):
            object.set_created_date()
        object.set_updated_date()

    def validate_has_id(self, object: object):
        if not hasattr(object, "_id"):
            raise Exception("object must have _id field")

    def get_id_criteria(self, object):
        return {
            "_id": object._id
        }

    # Save all the fields from the object into mongo
    def get_update_query(self, object):
        return {
            "$set": self.serializer.serialize(object)
        }
