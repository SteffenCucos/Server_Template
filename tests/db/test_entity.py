from dataclasses import dataclass

from server.db.serializing_middleware import (
    get_application_deserializer,
    get_application_serializer,
)
from server.models.base.entity import Entity

serializer = get_application_serializer()
deserializer  = get_application_deserializer()

def test_entity():
    @dataclass
    class TestEntity(Entity()):
        a: int

    entity = TestEntity(a=10)

    assert entity.a == 10
    assert hasattr(entity, "id")
    assert hasattr(entity, "created_date")
    assert hasattr(entity, "updated_date")

    serialized = serializer.serialize(entity)
    deserialized: TestEntity = deserializer.deserialize(serialized, TestEntity)
    id = deserialized.id
    assert deserialized.a == 10
    assert deserialized.id == id


def test_id_entity():
    @dataclass
    class TestEntity(Entity("b")):
        a: int
        b: str

    entity = TestEntity(a=10, b="bId")

    assert entity.a == 10
    assert entity.b == "bId"
    assert entity.id == entity.b
    assert hasattr(entity, "created_date")
    assert hasattr(entity, "updated_date")
