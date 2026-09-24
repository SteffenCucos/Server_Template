
from __future__ import annotations

from abc import ABC
from dataclasses import MISSING, dataclass
from dataclasses import Field as DataclassField
from typing import TYPE_CHECKING, Any, Generic, TypeVar


from .ast_data_types import DataType, DataTypeT
from .exceptions import FieldParsingException


if TYPE_CHECKING:
    from .ast_table import ASTTable, IASTTable, TableTypeT
    from .ast_data_types import IDataType

FieldTypeT = TypeVar("FieldTypeT", bound=IASTField)


@dataclass
class IASTField(ABC, Generic[DataTypeT, TableTypeT, FieldTypeT]):
    name: str
    data_type: DataTypeT
    is_primary_key: bool = False
    is_nullable: bool = True
    default_value: Any | None = None
    is_unique: bool = False
    check_constraint: str | None = None
    foreign_key: tuple[TableTypeT, FieldTypeT] | str | None = None

    @classmethod
    def from_ast_field[D: IDataType, T: IASTTable, F: IASTField](
        cls: type[F], 
        field: ASTField, 
        data_cls: type[IDataType[D]]
    ) -> F:
        converted_type = data_cls.data_type_to_supported_backing_type(field.data_type)
        
        return cls(
            name=field.name,
            data_type=converted_type,
            is_primary_key=field.is_primary_key,
            is_nullable=field.is_nullable,
            default_value=field.default_value,
            is_unique=field.is_unique,
            check_constraint=field.check_constraint,
            # FK will be set manually in a second pass
        )


@dataclass
class ASTField(IASTField[DataType, ASTTable, 'ASTField']):
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
