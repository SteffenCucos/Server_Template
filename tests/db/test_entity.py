from dataclasses import dataclass
import pytest

from pserialize import serialize, deserialize

from server.models.entity import Entity


def test_entity():
    @dataclass
    class TestEntity(Entity()):
        a: int

    entity = TestEntity(a=10)

    assert entity.a == 10
    assert hasattr(entity, "_id")
    assert hasattr(entity, "_created_date")
    assert hasattr(entity, "_updated_date")


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
