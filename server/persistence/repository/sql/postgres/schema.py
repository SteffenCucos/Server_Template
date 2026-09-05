
from models.base.entity import IdEntity

from .ast.parse import parse_entities_to_tables


def generate_schema_ddl_operations(entity_types: list[type[IdEntity]]) -> list[str]:
    """
    Generate a list of DDL statements for creating tables and establishing relationships based on the provided entity types.
    """
    tables = parse_entities_to_tables(entity_types)
    # First pass, create tables
    ddl_operations: list[str] = []
    for table in tables:
        ddl_operations.append(table.create_table_ddl())

    # Second pass, create relationships (foreign keys)
    for table in tables:
        update_ddl = table.update_ddl()
        if update_ddl:
            ddl_operations.append(update_ddl)

    return ddl_operations