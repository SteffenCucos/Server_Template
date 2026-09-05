

import datetime

from enum import StrEnum
from types import NoneType, UnionType
from typing import Union, get_args, get_origin


class DataType(StrEnum):
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

    def is_text_type(self) -> bool:
        return self in {DataType.TEXT, DataType.VARCHAR}

    @staticmethod
    def from_python_type(py_type: type) -> tuple['DataType', bool]:
        """
        Maps Python types to PostgreSQL data types.
        """
        is_nullable = False
        if get_origin(py_type) in (Union, UnionType):
            is_nullable = True
            types = [t for t in get_args(py_type) if t is not NoneType]
            if len(types) == 1:
                py_type = types[0]
            else:
                raise ValueError(f"Unsupported Python type for mapping to PostgreSQL data type: {py_type}. Only single-type Optionals are supported.")
        db_type = None
        if py_type is str or issubclass(py_type, str):
            db_type = DataType.TEXT
        elif py_type is int:
            db_type = DataType.INTEGER
        elif py_type is float:
            db_type = DataType.DOUBLE_PRECISION
        elif py_type is bool:
            db_type = DataType.BOOLEAN
        elif py_type is dict:
            db_type = DataType.JSONB
        elif py_type is list:
            db_type = DataType.JSONB
        elif py_type is datetime.datetime:
            db_type = DataType.TIMESTAMP
        else:
            raise ValueError(f"Unsupported Python type for mapping to PostgreSQL data type: {py_type}")

        return db_type, is_nullable
