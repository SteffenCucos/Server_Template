from dataclasses import dataclass

import pytest
from server.db.serializing_middleware import (get_application_deserializer,
                                              get_application_serializer)
from server.models.base.entity import Entity

serializer = get_application_serializer()
deserializer  = get_application_deserializer()

def test_entity():
    @dataclass
    class TestEntity(Entity()):
        a: int

    entity = TestEntity(a=10)

    assert entity.a == 10
    assert hasattr(entity, "_id")
    assert hasattr(entity, "_created_date")
    assert hasattr(entity, "_updated_date")

    serialized = serializer.serialize(entity)
    deserialized: TestEntity = deserializer.deserialize(serialized, TestEntity)
    id = deserialized._id
    raise Exception(type(deserialized._id._id))


def test_id_entity():
    @dataclass
    class TestEntity(Entity("b")):
        a: int
        b: str

    entity = TestEntity(a=10, b="bId")

    assert entity.a == 10
    assert entity.b == "bId"
    assert entity._id == entity.b
    assert hasattr(entity, "_created_date")
    assert hasattr(entity, "_updated_date")
