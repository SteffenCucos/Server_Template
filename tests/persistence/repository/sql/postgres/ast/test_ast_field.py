
from dataclasses import dataclass, field, fields
from typing import Optional, Union, get_type_hints

import pytest

from server.persistence.repository.sql.postgres.ast.ast_data_types import DataType
from server.persistence.repository.sql.postgres.ast.ast_field import ASTField
from server.persistence.repository.sql.postgres.ast.exceptions import FieldParsingException


def test_from_dataclass_field_no_metadata_optional():
    @dataclass
    class TestClass:
        some_field: Optional[str] = field()

    hints = get_type_hints(TestClass)
    field_hint = hints["some_field"]
    some_field = [f for f in fields(TestClass)][0]

    ast_field = ASTField.from_dataclass_field(some_field, field_hint)

    assert ast_field.name == "some_field"
    assert ast_field.data_type == DataType.TEXT
    assert ast_field.is_nullable

    assert ast_field.to_column_definition() == '"some_field" TEXT'


def test_from_dataclass_field_no_metadata_union():
    @dataclass
    class TestClass:
        some_field: str | None = field()

    hints = get_type_hints(TestClass)
    field_hint = hints["some_field"]
    some_field = [f for f in fields(TestClass)][0]

    ast_field = ASTField.from_dataclass_field(some_field, field_hint)

    assert ast_field.name == "some_field"
    assert ast_field.data_type == DataType.TEXT
    assert ast_field.is_nullable

    assert ast_field.to_column_definition() == '"some_field" TEXT'


def test_from_dataclass_field_no_metadata_union_type():
    @dataclass
    class TestClass:
        some_field: Union[str, None] = field()

    hints = get_type_hints(TestClass)
    field_hint = hints["some_field"]
    some_field = [f for f in fields(TestClass)][0]

    ast_field = ASTField.from_dataclass_field(some_field, field_hint)

    assert ast_field.name == "some_field"
    assert ast_field.data_type == DataType.TEXT
    assert ast_field.is_nullable

    assert ast_field.to_column_definition() == '"some_field" TEXT'


def test_from_dataclass_field_metadata():
    @dataclass
    class TestClass:
        some_field: str = field(
            metadata={
                "primary_key": True,
                "nullable": False,
                "unique": True,
                "check": "Some Constraint SQL",
                "foreign_key": "sometable.field"
            },
            default="SomeDefaultValue"
        )

    hints = get_type_hints(TestClass)
    field_hint = hints["some_field"]
    some_field = [f for f in fields(TestClass)][0]

    ast_field = ASTField.from_dataclass_field(some_field, field_hint)

    assert ast_field.name == "some_field"
    assert ast_field.data_type == DataType.TEXT
    assert not ast_field.is_nullable
    assert ast_field.is_unique
    assert ast_field.check_constraint == "Some Constraint SQL"
    assert ast_field.foreign_key == "sometable.field"
    assert ast_field.default_value == "SomeDefaultValue"

    assert ast_field.to_column_definition() == '"some_field" TEXT PRIMARY KEY NOT NULL DEFAULT \'SomeDefaultValue\''


def test_from_dataclass_mismatched_metadata_type():
    @dataclass
    class TestClass:
        some_field: Optional[str] = field(
            metadata={
                "nullable": False,
            },
        )

    hints = get_type_hints(TestClass)
    field_hint = hints["some_field"]
    some_field = [f for f in fields(TestClass)][0]

    with pytest.raises(FieldParsingException, match="Field 'some_field' is marked as non nullable in its metadata but is typed as nullable in its class declaration"):
        _ = ASTField.from_dataclass_field(some_field, field_hint)
