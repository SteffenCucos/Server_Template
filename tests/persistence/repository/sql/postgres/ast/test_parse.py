from dataclasses import dataclass
from datetime import datetime
from typing import cast, override

import pytest

from server.auth.authorization_service import UserRole
from server.auth.rbac.models import Permission, Role, RolePermission
from server.models.base.entity import Entity, IdEntity
from server.models.base.id import Id
from server.persistence.models import CHECK, FOREIGN_KEY, NOT_NULLABLE, UNIQUE, field
from server.persistence.repository.sql.postgres.ast.ast_data_types import DataType
from server.persistence.repository.sql.postgres.ast.ast_table import ASTTable
from server.persistence.repository.sql.postgres.ast.exceptions import TableParsingException
from server.persistence.repository.sql.postgres.ast.parse import parse_entities_to_tables
from server.users.user import User


@dataclass
class Parent(Entity()):  # type: ignore[misc]
    name: str = field(NOT_NULLABLE)

    @staticmethod
    def table_name() -> str:
        return "parents"


def parse(*entities: type[IdEntity]) -> list[ASTTable]:
    return parse_entities_to_tables(list(entities))


@dataclass
class TypesEntity(Entity()):
    date_f: datetime
    float_f: float
    int_f: int
    str_f: str
    dict_f: dict
    list_f: list
    bool_f: bool

    @override
    @staticmethod
    def table_name() -> str:
        return "types_entities"


@dataclass
class ForeignKeyEntity(Entity()):
    target_id: Id = field(FOREIGN_KEY("types_entities.id"))

    @override
    @staticmethod
    def table_name() -> str:
        return "foreign_key_entities"


@dataclass
class UniqueEntity(Entity()):
    value: str = field(UNIQUE)

    @override
    @staticmethod
    def table_name() -> str:
        return "unique_entities"


@dataclass
class CheckEntity(Entity()):
    value: int = field(CHECK("value > 0"))

    @override
    @staticmethod
    def table_name() -> str:
        return "check_entities"


def test_parse_entities_to_tables_maps_python_types_to_ast_fields() -> None:
    table = parse(TypesEntity)[0]

    assert table.name == "types_entities"
    assert table.fields_by_name["id"].data_type is DataType.TEXT
    assert table.fields_by_name["id"].is_primary_key
    assert table.fields_by_name["created_date"].data_type is DataType.TIMESTAMP
    assert table.fields_by_name["updated_date"].data_type is DataType.TIMESTAMP
    assert {
        field_name: table.fields_by_name[field_name].data_type
        for field_name in ("date_f", "float_f", "int_f", "str_f", "dict_f", "list_f", "bool_f")
    } == {
        "date_f": DataType.TIMESTAMP,
        "float_f": DataType.DOUBLE_PRECISION,
        "int_f": DataType.INTEGER,
        "str_f": DataType.TEXT,
        "dict_f": DataType.JSONB,
        "list_f": DataType.JSONB,
        "bool_f": DataType.BOOLEAN,
    }


def test_parse_entities_to_tables_resolves_foreign_keys_to_ast_references() -> None:
    target_table, foreign_key_table = parse(TypesEntity, ForeignKeyEntity)

    foreign_key = foreign_key_table.fields_by_name["target_id"].foreign_key
    assert isinstance(foreign_key, tuple)
    assert foreign_key[0] is target_table
    assert foreign_key[1] is target_table.fields_by_name["id"]


def test_parse_entities_to_tables_preserves_unique_constraints() -> None:
    table = parse(UniqueEntity)[0]

    assert table.fields_by_name["value"].is_unique


def test_parse_entities_to_tables_preserves_check_constraints() -> None:
    table = parse(CheckEntity)[0]

    assert table.fields_by_name["value"].check_constraint == "value > 0"


def test_parse_entities_to_tables_resolves_role_permission_relationships() -> None:
    tables = parse(Permission, Role, RolePermission, User, UserRole)
    tables_by_name = {table.name: table for table in tables}

    assert set(tables_by_name) == {"permissions", "roles", "role_permissions", "users", "user_roles"}

    role_permission = tables_by_name["role_permissions"]
    role_foreign_key = role_permission.fields_by_name["role_id"].foreign_key
    permission_foreign_key = role_permission.fields_by_name["permission_id"].foreign_key
    assert role_foreign_key == (tables_by_name["roles"], tables_by_name["roles"].fields_by_name["id"])
    assert permission_foreign_key == (
        tables_by_name["permissions"],
        tables_by_name["permissions"].fields_by_name["id"],
    )

    user_role = tables_by_name["user_roles"]
    user_foreign_key = user_role.fields_by_name["user_id"].foreign_key
    assert user_foreign_key == (tables_by_name["users"], tables_by_name["users"].fields_by_name["id"])


def test_parse_entities_to_tables_rejects_non_string_foreign_keys() -> None:
    @dataclass
    class Child(Entity()):  # type: ignore[misc]
        parent_id: Id = field(NOT_NULLABLE | FOREIGN_KEY(cast(str, 1)))

        @staticmethod
        def table_name() -> str:
            return "children"

    with pytest.raises(TableParsingException, match="Foreign key must be a string"):
        parse(Parent, Child)


def test_parse_entities_to_tables_rejects_malformed_foreign_keys() -> None:
    @dataclass
    class Child(Entity()):  # type: ignore[misc]
        parent_id: Id = field(NOT_NULLABLE | FOREIGN_KEY("parents-id"))

        @staticmethod
        def table_name() -> str:
            return "children"

    with pytest.raises(TableParsingException, match="Foreign key must be a string"):
        parse(Parent, Child)


def test_parse_entities_to_tables_rejects_foreign_keys_to_unknown_tables() -> None:
    @dataclass
    class Child(Entity()):  # type: ignore[misc]
        parent_id: Id = field(NOT_NULLABLE | FOREIGN_KEY("unknown_parents.id"))

        @staticmethod
        def table_name() -> str:
            return "children"

    with pytest.raises(TableParsingException, match="Foreign key table 'unknown_parents' not found"):
        parse(Parent, Child)


def test_parse_entities_to_tables_rejects_foreign_keys_to_unknown_fields() -> None:
    @dataclass
    class Child(Entity()):  # type: ignore[misc]
        parent_id: Id = field(NOT_NULLABLE | FOREIGN_KEY("parents.unknown_id"))

        @staticmethod
        def table_name() -> str:
            return "children"

    with pytest.raises(TableParsingException, match="Foreign key field 'unknown_id' not found"):
        parse(Parent, Child)
