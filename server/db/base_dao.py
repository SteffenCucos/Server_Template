from typing import Any, Generic, TypeVar

from .config import DatabaseSettings
from .database import Database, DatabaseUpdate, IdValue
from .serializing_middleware import (
    get_application_deserializer,
    get_application_serializer,
)

T = TypeVar("T")


class BaseDAO(Generic[T]):
    """Backend-neutral DAO base class.

    BaseDAO serializes/deserializes application objects and delegates primitive
    persistence operations to Database. Database maps those operations to Mongo
    or Postgres based on DatabaseSettings without exposing driver-specific types.
    """

    def __init__(
        self,
        db: Database | None = None,
        resource_name: str | None = None,
        classType: type | None = None,
        settings: DatabaseSettings | None = None,
        id_field: str = "_id",
    ):
        self.classType = classType
        self.id_field = id_field
        self.serializer = get_application_serializer()
        self.deserializer = get_application_deserializer()
        self.db = db or Database(
            settings=settings,
            resource_name=resource_name or self._default_resource_name(classType),
            id_field=id_field,
        )

    def save(self, object: T) -> IdValue:
        return self.db.save(self.serializer.serialize(object))

    def save_many(self, lst: list[T]) -> list[IdValue]:
        serialized = self.serializer.serialize(lst)
        return self.db.save_many(serialized)

    def update(self, object: T) -> None:
        self.db.update(self.update_request(object))

    def update_request(self, object: T) -> DatabaseUpdate:
        return DatabaseUpdate(
            entity_id=str(self.get_entity_id(object)),
            values=self.get_update_record(object),
        )

    def update_many(self, lst: list[T]) -> None:
        self.db.update_many([self.update_request(object) for object in lst])

    def find_all(self) -> list[T]:
        records = self.db.find_all()
        return self.deserializer.deserialize(value=records, classType=list[self.classType])

    def find_one_by_condition(self, condition: dict[str, Any]) -> T | None:
        record = self.db.find_one(condition)
        if record:
            return self.deserializer.deserialize(value=record, classType=self.classType)
        return None

    def close(self) -> None:
        self.db.close()

    def get_update_record(self, object: T) -> dict[str, Any]:
        """Serialize an object into a backend-neutral record for updates."""
        return self.serializer.serialize(object)

    def get_update_query(self, object: T) -> dict[str, Any]:
        """Backward-compatible alias for get_update_record.

        This no longer returns a Mongo `$set` query. Concrete database adapters
        build backend-specific update statements internally.
        """
        return self.get_update_record(object)

    def get_id_criteria(self, entity: T) -> dict[str, Any]:
        return {self.id_field: self.get_entity_id(entity)}

    def get_entity_id(self, entity: T) -> Any:
        return getattr(entity, self.id_field)

    def _default_resource_name(self, classType: type | None) -> str:
        if classType is None:
            raise ValueError("BaseDAO requires either db, resource_name, or classType")
        return f"{classType.__name__.lower()}s"
