
import re

from typing import get_type_hints

from models.base.entity import IdEntity
from persistence.repository.sql.postgres.ast.pg_ast_data_types import PGDataType

from .ast_data_types import IDataType
from .ast_field import ASTField, IASTField
from .ast_table import ASTTable, IASTTable
from .exceptions import TableParsingException

from postgres.ast.pg_ast_table import PGASTField, PGASTTable


_foreign_key_pattern = re.compile(
    r"(?P<table>[A-Za-z_][A-Za-z0-9_]*)\.(?P<field>[A-Za-z_][A-Za-z0-9_]*)"
)


def parse_entities_to_tables(entities: list[type[IdEntity]]) -> list[ASTTable]:
    partially_resolved_tables: list[ASTTable] = [_entity_to_partial_table(entity) for entity in entities]
    tables_by_name: dict[str, ASTTable] = {table.name: table for table in partially_resolved_tables}
    # Establish relationships between tables based on the fields of the entities
    # At this point any FK will be a string of the form "table_name.field_name"
    for table in partially_resolved_tables:
        table_name = table.name
        fk_fields = [field for field in table.fields if field.foreign_key is not None]
        for fk_field in fk_fields:
            fk_str = fk_field.foreign_key
            if not isinstance(fk_str, str):
                raise TableParsingException("Foreign key must be a string of the form 'table.field'")

            match = _foreign_key_pattern.fullmatch(fk_str)
            if match is None:
                raise TableParsingException("Foreign key must be a string of the form 'table.field'")

            fk_table_name, fk_field_name = match["table"], match["field"]
            if fk_table_name not in tables_by_name:
                raise TableParsingException(f"Foreign key table '{fk_table_name}' not found for field '{fk_field.name}' in table '{table_name}'")

            fk_table = tables_by_name[fk_table_name]
            if fk_field_name not in fk_table.fields_by_name:
                raise TableParsingException(f"Foreign key field '{fk_field_name}' not found in table '{fk_table_name}' for field '{fk_field.name}' in table '{table_name}'")

            # Populate FK with the actual table and field references
            fk_field.foreign_key = (fk_table, fk_table.fields_by_name[fk_field_name])    

    # FKs are now resolved
    fully_resolved_tables = partially_resolved_tables
    return fully_resolved_tables


def transform_pg(ast_tables: list[ASTTable]) -> list[PGASTTable]:
   # PGASTTable.from_ast_table(ast_tables)
    x = transform(ast_tables, PGASTTable, PGASTField, PGDataType)
    return []


def transform[D: IDataType, T: IASTTable, F: IASTField](
        ast_tables: list[ASTTable], 
        table_cls: type[IASTTable[D, T, F]], 
        field_cls: type[F],
        data_cls: type[IDataType[D]]
) -> list[IASTTable[D, T, F]]:
    """
    Transform a list of ASTTables into a list of corresponding PG table ast nodes
    """

    partially_transformed_tables = [table_cls.from_ast_table(ast_table, field_cls, data_cls) for ast_table in ast_tables]
    pg_tables_by_name: dict[str, IASTTable[D, T, F]] = {table.name: table for table in partially_transformed_tables}
    ast_tables_by_name: dict[str, ASTTable] = {table.name: table for table in ast_tables}

    # Second pass to fix FKs
    for pg_table in partially_transformed_tables:
        table_name = pg_table.name
        ast_table = ast_tables_by_name[table_name]
        # transformed tables currently have no FK filled in, get it via the ast table
        ast_fields = [field for field in ast_table.fields if field.foreign_key is not None]
        for ast_field in ast_fields:
            pg_field = pg_table.fields_by_name[ast_field.name]
            fk = ast_field.foreign_key
            if isinstance(fk, str) or fk is None:
                raise TableParsingException(f"Expected FK to be parsed in transform")

            fk_ast_table, fk_ast_field = fk
            fk_pg_table = pg_tables_by_name[fk_ast_table.name]
            fk_pg_field = fk_pg_table.fields_by_name[fk_ast_field.name]

            pg_field.foreign_key = (fk_pg_table, fk_pg_field)

    # FKs are now resolved
    fully_transformed_tables = partially_transformed_tables
    return fully_transformed_tables


def _entity_to_partial_table(entity_type: type[IdEntity]) -> ASTTable:
    """
    First pass where we establish the table name and fields, but we haven't considered relationships yet.
    """
    table_name = entity_type.table_name()
    table = ASTTable(table_name)

    # Loop over the fields of the entity
    hints = get_type_hints(entity_type)
    for dataclass_field in entity_type.iterate_field_metadata():
        ast_field = ASTField.from_dataclass_field(dataclass_field, hints[dataclass_field.name])
        table.add_field(ast_field)

    return table
