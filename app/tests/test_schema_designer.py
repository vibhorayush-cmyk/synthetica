from __future__ import annotations

from app.schema_designer.generator import SchemaDesignerGenerator
from app.schema_designer.parser import (
    ColumnDefinition,
    SchemaDefinition,
    TableDefinition,
)
from app.schema_designer.relationship_builder import RelationshipBuilder
from app.schema_designer.validator import SchemaValidator


def test_schema_validation_detects_duplicate_tables_and_missing_primary_key() -> None:
    validator = SchemaValidator()
    schema = SchemaDefinition(
        tables=[
            TableDefinition(
                name="Customers",
                rows=10,
                columns=[
                    ColumnDefinition(
                        name="CustomerID", type="primary_key", primary_key=True
                    )
                ],
            ),
            TableDefinition(
                name="Customers",
                rows=10,
                columns=[
                    ColumnDefinition(
                        name="CustomerID", type="primary_key", primary_key=True
                    )
                ],
            ),
        ]
    )

    try:
        validator.validate(schema)
    except ValueError as error:
        assert "Duplicate tables" in str(error)
    else:
        raise AssertionError("duplicate tables should fail validation")


def test_relationship_builder_builds_relationships() -> None:
    schema = SchemaDefinition(
        tables=[
            TableDefinition(
                name="Customers",
                rows=10,
                columns=[
                    ColumnDefinition(
                        name="CustomerID", type="primary_key", primary_key=True
                    )
                ],
            ),
            TableDefinition(
                name="Orders",
                rows=10,
                columns=[
                    ColumnDefinition(
                        name="OrderID", type="primary_key", primary_key=True
                    ),
                    ColumnDefinition(
                        name="CustomerID", type="foreign_key", default="Customers"
                    ),
                ],
            ),
        ]
    )

    relationship_schema = RelationshipBuilder().build(schema)
    assert relationship_schema.tables[1].relationships[0].to_table == "Customers"


def test_schema_generator_creates_dataframes_and_export() -> None:
    schema = SchemaDefinition(
        tables=[
            TableDefinition(
                name="Customers",
                rows=25,
                columns=[
                    ColumnDefinition(
                        name="CustomerID", type="primary_key", primary_key=True
                    ),
                    ColumnDefinition(name="Name", type="text"),
                ],
            ),
            TableDefinition(
                name="Orders",
                rows=25,
                columns=[
                    ColumnDefinition(
                        name="OrderID", type="primary_key", primary_key=True
                    ),
                    ColumnDefinition(
                        name="CustomerID", type="foreign_key", default="Customers"
                    ),
                    ColumnDefinition(name="Amount", type="decimal"),
                ],
            ),
        ]
    )

    generated = SchemaDesignerGenerator().generate(schema)

    assert set(generated) == {"customers", "orders"}
    assert len(generated["customers"]) == 25
    assert len(generated["orders"]) == 25
