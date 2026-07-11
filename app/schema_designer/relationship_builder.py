from __future__ import annotations

from app.schema_designer.parser import (
    RelationshipDefinition,
    SchemaDefinition,
    TableDefinition,
)


class RelationshipBuilder:
    """Build relationships between tables from schema metadata."""

    def build(self, schema: SchemaDefinition) -> SchemaDefinition:
        tables = []
        for table in schema.tables:
            relationships = []
            for column in table.columns:
                if column.type == "foreign_key":
                    relationships.append(
                        RelationshipDefinition(
                            from_table=table.name,
                            to_table=column.default or "Customers",
                            from_column=column.name,
                            to_column="id",
                        )
                    )
            tables.append(
                TableDefinition(
                    name=table.name,
                    rows=table.rows,
                    columns=table.columns,
                    relationships=relationships,
                )
            )
        return SchemaDefinition(tables=tables)
