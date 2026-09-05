
import re

from typing import get_type_hints

from models.base.entity import IdEntity

from .ast_field import ASTField
from .ast_table import ASTTable
from .exceptions import TableParsingException

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
