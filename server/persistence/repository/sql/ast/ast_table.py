
from __future__ import annotations
from abc import ABC, abstractmethod


from typing import TYPE_CHECKING, Generic, TypeVar

from persistence.repository.sql.ast.ast_data_types import IDataType
from persistence.repository.sql.ast.ast_field import IASTField

if TYPE_CHECKING:
    from .ast_field import ASTField, FieldTypeT
    from .ast_data_types import DataType, DataTypeT

TableTypeT = TypeVar("TableTypeT", bound=IASTTable)


class IASTTable(ABC,Generic[DataTypeT, TableTypeT, FieldTypeT]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.fields: list[FieldTypeT] = []
        self.fields_by_name: dict[str, FieldTypeT] = {}

    def add_field(self, field: FieldTypeT) -> None:
        self.fields.append(field)
        self.fields_by_name[field.name] = field

    @abstractmethod
    @classmethod
    def from_ast_table[D: IDataType, T: IASTTable, F: IASTField](
        cls: type[IASTTable[D,T,F]], 
        ast_table: ASTTable, 
        field_cls: type[F], 
        data_cls: type[IDataType[D]]
    ) -> IASTTable[D, T ,F]:
        table = cls(ast_table.name)
        for ast_field in ast_table.fields:
            field = field_cls.from_ast_field(ast_field, data_cls)
            table.add_field(field)

        return table

class ASTTable(IASTTable[DataType, 'ASTTable', ASTField]):
    pass

