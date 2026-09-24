

from enum import StrEnum
from typing import override

from persistence.repository.sql.ast.ast_data_types import DataType, IDataType


class PGDataType(StrEnum, IDataType['PGDataType']):
    """
    Subset of PostgreSQL data types that are supported by the persistence layer.
    https://www.postgresql.org/docs/current/datatype.html
    """
    # Character Types
    TEXT = "TEXT"
    VARCHAR = "VARCHAR"

    # Numeric Types
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    DECIMAL = "DECIMAL"
    NUMERIC = "NUMERIC"
    REAL = "REAL"
    DOUBLE_PRECISION = "DOUBLE PRECISION"

    # Boolean Type
    BOOLEAN = "BOOLEAN"

    # Date/Time Types
    TIMESTAMP = "TIMESTAMP"
    DATE = "DATE"
    TIME = "TIME"

    # UUID
    UUID = "UUID"

    # JSON Types
    JSON = "JSON"
    JSONB = "JSONB"

    @override
    def is_text_type(self) -> bool:
        return self in {PGDataType.TEXT, PGDataType.VARCHAR}

    @override
    @staticmethod
    def data_type_to_supported_backing_type(data_type: DataType) -> PGDataType:
        match data_type:
            case DataType.TEXT: return PGDataType.TEXT
            case DataType.VARCHAR: return PGDataType.VARCHAR
            case DataType.INTEGER: return PGDataType.INTEGER
            case DataType.BIGINT: return PGDataType.BIGINT
            case DataType.DECIMAL: return PGDataType.DECIMAL
            case DataType.NUMERIC: return PGDataType.NUMERIC
            case DataType.REAL: return PGDataType.REAL
            case DataType.DOUBLE_PRECISION: return PGDataType.DOUBLE_PRECISION
            case DataType.BOOLEAN: return PGDataType.BOOLEAN
            case DataType.TIMESTAMP: return PGDataType.TIMESTAMP
            case DataType.DATE: return PGDataType.DATE
            case DataType.TIME: return PGDataType.TIME
            case DataType.UUID: return PGDataType.UUID
            case DataType.JSON: return PGDataType.JSON
            case DataType.JSONB: return PGDataType.JSONB
            case _:
                raise ValueError(f"Unsupported PostgreSQL data type: {data_type}")
    
