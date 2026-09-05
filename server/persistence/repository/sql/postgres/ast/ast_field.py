
from __future__ import annotations

from dataclasses import MISSING, dataclass
from dataclasses import Field as DataclassField
from typing import TYPE_CHECKING, Any

from .ast_data_types import DataType
from .exceptions import FieldParsingException

if TYPE_CHECKING:
    from .ast_table import ASTTable


@dataclass
class ASTField:
    name: str
    data_type: DataType
    is_primary_key: bool = False
    is_nullable: bool = True
    default_value: Any | None = None
    is_unique: bool = False
    check_constraint: str | None = None
    foreign_key: tuple[ASTTable, 'ASTField'] | str | None = None

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
    def from_dataclass_field(dataclass_field: DataclassField[object], type_hint: type) -> 'ASTField':
        metadata = dataclass_field.metadata
        data_type, is_nullable_type = DataType.from_python_type(type_hint)

        if metadata is None:
            return ASTField(
                name=dataclass_field.name,
                data_type=data_type,
                is_nullable=is_nullable_type
            )

        is_nullable_metadata = dataclass_field.metadata.get("nullable", True)
        if not is_nullable_metadata and is_nullable_type:
            raise FieldParsingException(
                f"Field '{dataclass_field.name}' is marked as non nullable in its metadata but is typed as nullable in its class declaration")
        
        is_primary_key = dataclass_field.metadata.get("primary_key", False)
        is_nullable = is_nullable_metadata or is_nullable_type
        default_value = dataclass_field.default if dataclass_field.default else None
        is_unique = dataclass_field.metadata.get("unique", False)
        check_constraint = dataclass_field.metadata.get("check", None)
        foreign_key = dataclass_field.metadata.get("foreign_key", None)

        return ASTField(
            name=dataclass_field.name,
            data_type=data_type,
            is_primary_key=is_primary_key,
            is_nullable=is_nullable,
            default_value=default_value,
            is_unique=is_unique,
            check_constraint=check_constraint,
            foreign_key=foreign_key,
        )
