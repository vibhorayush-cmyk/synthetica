from __future__ import annotations

from collections.abc import Iterable

from app.schema_designer.parser import (
    RelationshipDefinition,
    SchemaDefinition,
    TableDefinition,
)


class SchemaValidator:
    """Validate schema structure before data generation."""

    def validate(self, schema: SchemaDefinition) -> None:
        table_names = {table.name for table in schema.tables}
        if len(table_names) != len(schema.tables):
            raise ValueError("Duplicate tables are not allowed")

        for table in schema.tables:
            column_names = {column.name for column in table.columns}
            if len(column_names) != len(table.columns):
                raise ValueError(
                    f"Duplicate columns are not allowed in table {table.name}"
                )

            primary_keys = [column for column in table.columns if column.primary_key]
            if len(primary_keys) > 1:
                raise ValueError(
                    f"Table {table.name} cannot have multiple primary keys"
                )
            if not primary_keys and table.name.lower() != "settings":
                raise ValueError(f"Missing primary key in table {table.name}")

        for table in schema.tables:
            for relationship in self._relationships_for_table(table):
                if (
                    relationship.from_table not in table_names
                    or relationship.to_table not in table_names
                ):
                    raise ValueError("Relationship references unknown table")
                if relationship.from_column not in {
                    column.name
                    for column in self._table_by_name(
                        schema.tables, relationship.from_table
                    ).columns
                }:
                    raise ValueError("Invalid foreign key source column")
                if relationship.to_column not in {
                    column.name
                    for column in self._table_by_name(
                        schema.tables, relationship.to_table
                    ).columns
                }:
                    raise ValueError("Invalid foreign key target column")

        self._validate_circular_relationships(schema)

    def _validate_circular_relationships(self, schema: SchemaDefinition) -> None:
        graph: dict[str, list[str]] = {
            table.name: [rel.to_table for rel in self._relationships_for_table(table)]
            for table in schema.tables
        }
        visited: set[str] = set()
        stack: list[str] = []

        def visit(node: str) -> None:
            if node in stack:
                raise ValueError("Circular relationships are not allowed")
            if node in visited:
                return
            visited.add(node)
            stack.append(node)
            for neighbor in graph.get(node, []):
                visit(neighbor)
            stack.pop()

        for table in graph:
            visit(table)

    @staticmethod
    def _table_by_name(tables: Iterable[TableDefinition], name: str) -> TableDefinition:
        return next(table for table in tables if table.name == name)

    @staticmethod
    def _relationships_for_table(
        table: TableDefinition,
    ) -> list[RelationshipDefinition]:
        return table.relationships or []
