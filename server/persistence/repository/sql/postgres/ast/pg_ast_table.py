
from persistence.repository.sql.ast.ast_table import ASTTable, IASTTable


from .pg_ast_field import PGASTField
from .pg_ast_data_types import PGDataType

class PGASTTable(IASTTable[PGDataType, 'PGASTTable', PGASTField]):

    def create_table_ddl(self) -> str:
        field_definitions = ",\n  ".join(field.to_column_definition() for field in self.fields)
        return f"CREATE TABLE {self.name} (\n  {field_definitions}\n);"

    def update_ddl(self) -> str | None:
        fk_assignments = self._foreign_keys_ddl()
        unique_assignments = self._unique_constraints_ddl()
        check_assignments = self._check_constraints_ddl()
        all_assignments = fk_assignments + unique_assignments + check_assignments
        if not all_assignments:
            return None
        return f"ALTER TABLE {self.name}\n " + ",\n  ".join(all_assignments) + ";"

    def _foreign_keys_ddl(self) -> list[str]:
        fk_assignments: list[str] = []
        for field in self.fields:
            if isinstance(field.foreign_key, tuple):
                fk_table, fk_field = field.foreign_key
                fk_assignments.append(f"ADD CONSTRAINT fk_{self.name}_{fk_table.name} FOREIGN KEY ({field.name}) REFERENCES {fk_table.name}({fk_field.name})")

        return fk_assignments

    def _unique_constraints_ddl(self) -> list[str]:
        unique_assignments: list[str] = []
        for field in self.fields:
            if field.is_unique:
                unique_assignments.append(f"ADD CONSTRAINT uq_{self.name}_{field.name} UNIQUE ({field.name})")

        return unique_assignments

    def _check_constraints_ddl(self) -> list[str]:
        check_assignments: list[str] = []
        for field in self.fields:
            if field.check_constraint is not None:
                check_assignments.append(f"ADD CONSTRAINT chk_{self.name}_{field.name} CHECK ({field.check_constraint})")

        return check_assignments
