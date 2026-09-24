
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sqlite_ast_field import SQLiteASTField


class SQLiteASTTable:
    def __init__(self, name: str) -> None:
        self.name = name
        self.fields: list[SQLiteASTField] = []
        self.fields_by_name: dict[str, SQLiteASTField] = {}

    def add_field(self, field: SQLiteASTField) -> None:
        self.fields.append(field)
        self.fields_by_name[field.name] = field

