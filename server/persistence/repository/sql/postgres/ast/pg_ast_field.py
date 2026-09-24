
from __future__ import annotations

from dataclasses import MISSING, dataclass
from dataclasses import Field as DataclassField
from typing import TYPE_CHECKING, Any

from typing_extensions import override


from persistence.repository.sql.ast.ast_field import ASTField, IASTField
from persistence.repository.sql.ast.ast_table import ASTTable

from .pg_ast_data_types import PGDataType
from .pg_ast_table import PGASTTable


@dataclass
class PGASTField(IASTField[PGDataType, PGASTTable, 'PGASTField']):

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

