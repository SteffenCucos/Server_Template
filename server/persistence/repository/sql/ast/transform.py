

from typing import TypeVar

from .ast_table import ASTTable
from .exceptions import TableParsingException

from ..postgres.ast.pg_ast_table import PGASTTable


def transform(ast_tables: list[ASTTable]) -> list[PGASTTable]:
    """
    Transform a list of ASTTables into a list of corresponding PG table ast nodes
    """

    partially_transformed_tables = [PGASTTable.from_ast_table(ast_table) for ast_table in ast_tables]
    pg_tables_by_name: dict[str, PGASTTable] = {table.name: table for table in partially_transformed_tables}
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