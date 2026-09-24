from dataclasses import dataclass
from datetime import datetime
from typing import cast, override

import pytest

from server.auth.authorization_service import UserRole
from server.auth.rbac.models import Permission, Role, RolePermission
from server.models.base.entity import Entity
from server.models.base.id import Id
from server.persistence.models import CHECK, FOREIGN_KEY, UNIQUE, field
from server.persistence.repository.sql.postgres.ast.exceptions import TableParsingException
from server.persistence.repository.sql.postgres.schema import generate_schema_ddl_operations
from server.users.user import User

# Region Test Types

@dataclass
class TestTypesEntity(Entity()):
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
        return "test_types_entities"


@dataclass
class TestFKEntity(Entity()):
    fk_field: str = field(FOREIGN_KEY("test_types_entities.id"))

    @override
    @staticmethod
    def table_name() -> str:
        return "test_fk_entities"


@dataclass
class TestUniqueEntity(Entity()):
    unique_field: str = field(UNIQUE)

    @override
    @staticmethod
    def table_name() -> str:
        return "test_unique_entities"


@dataclass
class TestCheckConstraintEntity(Entity()):
    check_field: int = field(CHECK("check_field > 0"))

    @override
    @staticmethod
    def table_name() -> str:
        return "test_check_constraint_entities"

# Region Tests

def test_generate_schema_ddl_operations_creates_proper_types() -> None:
    operations = generate_schema_ddl_operations([TestTypesEntity])
    assert operations[0] == (
        'CREATE TABLE test_types_entities (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "date_f" TIMESTAMP,\n'
        '  "float_f" DOUBLE PRECISION,\n'
        '  "int_f" INTEGER,\n'
        '  "str_f" TEXT,\n'
        '  "dict_f" JSONB,\n'
        '  "list_f" JSONB,\n'
        '  "bool_f" BOOLEAN\n'
        ');'
    )


def test_generate_schema_ddl_operations_creates_foreign_keys() -> None:
    operations = generate_schema_ddl_operations([TestTypesEntity, TestFKEntity])
    assert operations[0] == (
        'CREATE TABLE test_types_entities (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "date_f" TIMESTAMP,\n'
        '  "float_f" DOUBLE PRECISION,\n'
        '  "int_f" INTEGER,\n'
        '  "str_f" TEXT,\n'
        '  "dict_f" JSONB,\n'
        '  "list_f" JSONB,\n'
        '  "bool_f" BOOLEAN\n'
        ');'
    )
    assert operations[1] == (
        'CREATE TABLE test_fk_entities (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "fk_field" TEXT\n'
        ');'
    )
    assert operations[2] == (
        "ALTER TABLE test_fk_entities\n "
        "ADD CONSTRAINT fk_test_fk_entities_test_types_entities FOREIGN KEY (fk_field) REFERENCES test_types_entities(id);"
    )


def test_generate_schema_ddl_operations_creates_unique_constraints() -> None:
    operations = generate_schema_ddl_operations([TestUniqueEntity])
    assert operations[0] == (
        'CREATE TABLE test_unique_entities (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "unique_field" TEXT\n'
        ');'
    )
    assert operations[1] == (
        "ALTER TABLE test_unique_entities\n "
        "ADD CONSTRAINT uq_test_unique_entities_unique_field UNIQUE (unique_field);"
    )


def test_generate_schema_ddl_operations_creates_check_constraints() -> None:
    operations = generate_schema_ddl_operations([TestCheckConstraintEntity])
    assert operations[0] == (
        'CREATE TABLE test_check_constraint_entities (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "check_field" INTEGER\n'
        ');'
    )
    assert operations[1] == (
        "ALTER TABLE test_check_constraint_entities\n "
        "ADD CONSTRAINT chk_test_check_constraint_entities_check_field CHECK (check_field > 0);"
    )


def test_generate_schema_ddl_operations_creates_role_permission_foreign_keys() -> None:
    operations = generate_schema_ddl_operations([Permission, Role, RolePermission, User, UserRole])
    assert operations[:5] == [
        'CREATE TABLE permissions (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "key" TEXT NOT NULL,\n'
        '  "description" TEXT DEFAULT NULL\n'
        ');',
        'CREATE TABLE roles (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "name" TEXT NOT NULL,\n'
        '  "description" TEXT DEFAULT NULL\n'
        ');',
        'CREATE TABLE role_permissions (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "role_id" TEXT NOT NULL,\n'
        '  "permission_id" TEXT NOT NULL\n'
        ');',
        'CREATE TABLE users (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "user_name" TEXT NOT NULL,\n'
        '  "first_name" TEXT NOT NULL,\n'
        '  "last_name" TEXT NOT NULL,\n'
        '  "password_hash" TEXT NOT NULL,\n'
        '  "email" TEXT NOT NULL,\n'
        '  "email_verified" BOOLEAN DEFAULT NULL\n'
        ');',
        'CREATE TABLE user_roles (\n'
        '  "id" TEXT PRIMARY KEY,\n'
        '  "created_date" TIMESTAMP,\n'
        '  "updated_date" TIMESTAMP,\n'
        '  "user_id" TEXT NOT NULL,\n'
        '  "role_id" TEXT NOT NULL\n'
        ');',
    ]
    assert operations[5:] == [
        "ALTER TABLE roles\n "
        "ADD CONSTRAINT uq_roles_name UNIQUE (name);",

        "ALTER TABLE role_permissions\n "
        "ADD CONSTRAINT fk_role_permissions_roles FOREIGN KEY (role_id) REFERENCES roles(id),\n  "
        "ADD CONSTRAINT fk_role_permissions_permissions FOREIGN KEY (permission_id) REFERENCES permissions(id);",

        "ALTER TABLE users\n "
        "ADD CONSTRAINT uq_users_email UNIQUE (email);",

        "ALTER TABLE user_roles\n "
        "ADD CONSTRAINT fk_user_roles_users FOREIGN KEY (user_id) REFERENCES users(id),\n  "
        "ADD CONSTRAINT fk_user_roles_roles FOREIGN KEY (role_id) REFERENCES roles(id);"
    ]


def test_generate_schema_ddl_operations_rejects_non_string_foreign_keys() -> None:
    @dataclass
    class InvalidForeignKeyEntity(Entity()):
        target_id: Id = field(FOREIGN_KEY(cast(str, 1)))

        @staticmethod
        def table_name() -> str:
            return "invalid_foreign_key_entities"

    with pytest.raises(TableParsingException, match="Foreign key must be a string"):
        generate_schema_ddl_operations([TestTypesEntity, InvalidForeignKeyEntity])


def test_generate_schema_ddl_operations_rejects_malformed_foreign_keys() -> None:
    @dataclass
    class InvalidForeignKeyEntity(Entity()):
        target_id: Id = field(FOREIGN_KEY("test_types_entities-id"))

        @staticmethod
        def table_name() -> str:
            return "invalid_foreign_key_entities"

    with pytest.raises(TableParsingException, match="Foreign key must be a string"):
        generate_schema_ddl_operations([TestTypesEntity, InvalidForeignKeyEntity])


def test_generate_schema_ddl_operations_rejects_foreign_keys_to_unknown_tables() -> None:
    @dataclass
    class InvalidForeignKeyEntity(Entity()):
        target_id: Id = field(FOREIGN_KEY("unknown_table.id"))

        @staticmethod
        def table_name() -> str:
            return "invalid_foreign_key_entities"

    with pytest.raises(TableParsingException, match="Foreign key table 'unknown_table' not found"):
        generate_schema_ddl_operations([TestTypesEntity, InvalidForeignKeyEntity])


def test_generate_schema_ddl_operations_rejects_foreign_keys_to_unknown_fields() -> None:
    @dataclass
    class InvalidForeignKeyEntity(Entity()):
        target_id: Id = field(FOREIGN_KEY("test_types_entities.unknown_id"))

        @staticmethod
        def table_name() -> str:
            return "invalid_foreign_key_entities"

    with pytest.raises(TableParsingException, match="Foreign key field 'unknown_id' not found"):
        generate_schema_ddl_operations([TestTypesEntity, InvalidForeignKeyEntity])
