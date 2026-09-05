from dataclasses import MISSING

from server.persistence.repository.sql.postgres.ast.ast_data_types import DataType
from server.persistence.repository.sql.postgres.ast.ast_field import ASTField
from server.persistence.repository.sql.postgres.ast.ast_table import ASTTable


def test_create_table_ddl_for_plain_table() -> None:
    table = ASTTable("users")
    table.add_field(ASTField("id", DataType.TEXT, is_primary_key=True, default_value=MISSING))
    table.add_field(ASTField("name", DataType.TEXT, is_nullable=False, default_value=MISSING))

    assert table.create_table_ddl() == (
        "CREATE TABLE users (\n"
        '  "id" TEXT PRIMARY KEY,\n'
        '  "name" TEXT NOT NULL\n'
        ");"
    )
    assert table.update_ddl() is None


def test_update_ddl_creates_foreign_key_constraint() -> None:
    parent = ASTTable("parents")
    parent_id = ASTField("id", DataType.TEXT, is_primary_key=True, default_value=MISSING)
    parent.add_field(parent_id)

    table = ASTTable("children")
    table.add_field(ASTField("parent_id", DataType.TEXT, default_value=MISSING, foreign_key=(parent, parent_id)))

    assert table.update_ddl() == (
        "ALTER TABLE children\n "
        "ADD CONSTRAINT fk_children_parents FOREIGN KEY (parent_id) REFERENCES parents(id);"
    )


def test_update_ddl_creates_unique_constraint() -> None:
    table = ASTTable("users")
    table.add_field(ASTField("email", DataType.TEXT, is_unique=True, default_value=MISSING))

    assert table.update_ddl() == "ALTER TABLE users\n ADD CONSTRAINT uq_users_email UNIQUE (email);"


def test_update_ddl_creates_check_constraint() -> None:
    table = ASTTable("products")
    table.add_field(ASTField("price", DataType.INTEGER, check_constraint="price > 0", default_value=MISSING))

    assert table.update_ddl() == "ALTER TABLE products\n ADD CONSTRAINT chk_products_price CHECK (price > 0);"


def test_update_ddl_creates_foreign_key_unique_and_check_constraints() -> None:
    parent = ASTTable("accounts")
    parent_id = ASTField("id", DataType.TEXT, is_primary_key=True, default_value=MISSING)
    parent.add_field(parent_id)

    table = ASTTable("users")
    table.add_field(ASTField("account_id", DataType.TEXT, default_value=MISSING, foreign_key=(parent, parent_id)))
    table.add_field(ASTField("email", DataType.TEXT, is_unique=True, default_value=MISSING))
    table.add_field(ASTField("age", DataType.INTEGER, check_constraint="age >= 18", default_value=MISSING))

    assert table.update_ddl() == (
        "ALTER TABLE users\n "
        "ADD CONSTRAINT fk_users_accounts FOREIGN KEY (account_id) REFERENCES accounts(id),\n  "
        "ADD CONSTRAINT uq_users_email UNIQUE (email),\n  "
        "ADD CONSTRAINT chk_users_age CHECK (age >= 18);"
    )
