from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ColumnDefinition:
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    default: Any = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    enum_values: list[str] | None = None


@dataclass(frozen=True, slots=True)
class RelationshipDefinition:
    from_table: str
    to_table: str
    from_column: str
    to_column: str


@dataclass(frozen=True, slots=True)
class TableDefinition:
    name: str
    rows: int
    columns: list[ColumnDefinition]
    relationships: list[RelationshipDefinition] = None

    def __post_init__(self) -> None:
        if self.relationships is None:
            object.__setattr__(self, "relationships", [])


@dataclass(frozen=True, slots=True)
class SchemaDefinition:
    tables: list[TableDefinition]


class SchemaDesignerParser:
    """Parse a JSON schema definition into typed objects."""

    def parse(self, payload: dict[str, Any]) -> SchemaDefinition:
        tables_payload = payload.get("tables", [])
        tables = []
        for table_payload in tables_payload:
            columns = []
            for column_payload in table_payload.get("columns", []):
                columns.append(
                    ColumnDefinition(
                        name=column_payload["name"],
                        type=column_payload.get("type", "text"),
                        nullable=column_payload.get("nullable", True),
                        primary_key=column_payload.get("primary_key", False),
                        default=column_payload.get("default"),
                        min_value=column_payload.get("min_value"),
                        max_value=column_payload.get("max_value"),
                        enum_values=column_payload.get("enum_values"),
                    )
                )
            tables.append(
                TableDefinition(
                    name=table_payload["name"],
                    rows=int(table_payload.get("rows", 100)),
                    columns=columns,
                )
            )
        return SchemaDefinition(tables=tables)
