

from enum import StrEnum
from typing import override

from persistence.repository.sql.ast.ast_data_types import DataType, IDataType


class SQLiteDataType(StrEnum, IDataType['SQLiteDataType']):
    """
    Subset of SQLite data types that are supported by the persistence layer.
    https://www.sqlite.org/datatype3.html
    """
    # Character Types
    TEXT = "TEXT"

    # Numeric Types
    INTEGER = "INTEGER"
    REAL = "REAL"

    # Blob Types
    BLOB = "BLOB"

    @override
    def is_text_type(self) -> bool:
        return self == SQLiteDataType.TEXT

    @override
    @staticmethod
    def data_type_to_supported_backing_type(data_type: DataType) -> SQLiteDataType:
        match data_type:
            case DataType.TEXT: return SQLiteDataType.TEXT
            case DataType.VARCHAR: return SQLiteDataType.TEXT
            case DataType.INTEGER: return SQLiteDataType.INTEGER
            case DataType.BIGINT: return SQLiteDataType.INTEGER
            case DataType.DECIMAL: return SQLiteDataType.REAL
            case DataType.NUMERIC: return SQLiteDataType.REAL
            case DataType.REAL: return SQLiteDataType.REAL
            case DataType.DOUBLE_PRECISION: return SQLiteDataType.REAL
            case DataType.BOOLEAN: return SQLiteDataType.INTEGER
            case DataType.TIMESTAMP: return SQLiteDataType.INTEGER
            case DataType.DATE: return SQLiteDataType.TEXT
            case DataType.TIME: return SQLiteDataType.INTEGER
            case DataType.UUID: return SQLiteDataType.TEXT
            case DataType.JSON: return SQLiteDataType.BLOB
            case DataType.JSONB: return SQLiteDataType.BLOB
            case _:
                raise ValueError(f"Unsupported SQLite data type: {data_type}")
    
