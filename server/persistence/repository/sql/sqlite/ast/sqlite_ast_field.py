
from __future__ import annotations

from dataclasses import MISSING, dataclass
from dataclasses import Field as DataclassField
from typing import TYPE_CHECKING, Any

from typing_extensions import override

from persistence.repository.sql.ast.ast_field import ASTField
from persistence.repository.sql.ast.ast_table import ASTTable

from .sqlite_ast_data_types import SQLiteDataType
from .sqlite_ast_table import SQLiteASTTable


@dataclass
class SQLiteASTField:
    name: str
    data_type: SQLiteDataType
    is_primary_key: bool = False
    is_nullable: bool = True
    default_value: Any | None = None
    is_unique: bool = False
    check_constraint: str | None = None
    foreign_key: tuple[SQLiteASTTable, 'SQLiteDataType'] | None = None

    def to_column_definition(self) -> str:
        sql = f'"{self.name}" {self.data_type.value}'
        if self.is_primary_key:
            sql += " PRIMARY KEY"
        if not self.is_nullable:
            sql += " NOT NULL"
        if self.default_value is not MISSING and self.default_value is not None:
            if self.data_type.is_text_type() and isinstance(self.default_value, str):
                sql += f" DEFAULT '{self.default_value}'"
            else:
                sql += f" DEFAULT {self.default_value}"
        if self.default_value is None:
            sql += " DEFAULT NULL"

        return sql

    @staticmethod
    def from_ast_field(field: ASTField):
        converted_type = SQLiteDataType.data_type_to_supported_backing_type(field.data_type)

        return SQLiteASTField(
            name=field.name,
            data_type=converted_type,
            is_primary_key=field.is_primary_key,
            is_nullable=field.is_nullable,
            default_value=field.default_value,
            is_unique=field.is_unique,
            check_constraint=field.check_constraint,
            # FK will be set manually in a second pass
        )