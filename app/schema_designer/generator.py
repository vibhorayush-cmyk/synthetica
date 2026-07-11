from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from faker import Faker

from app.challenges.base import ChallengePack
from app.exporters import ExportService
from app.schema_designer.parser import (
    ColumnDefinition,
    SchemaDefinition,
    TableDefinition,
)
from app.schema_designer.relationship_builder import RelationshipBuilder
from app.schema_designer.validator import SchemaValidator


class SchemaDesignerGenerator:
    """Generate tables and exports from a schema designer definition."""

    def __init__(
        self,
        validator: SchemaValidator | None = None,
        relationship_builder: RelationshipBuilder | None = None,
    ) -> None:
        self._validator = validator or SchemaValidator()
        self._relationship_builder = relationship_builder or RelationshipBuilder()
        self._faker = Faker()
        self._rng = np.random.default_rng(42)

    def generate(self, schema: SchemaDefinition) -> dict[str, pd.DataFrame]:
        self._validator.validate(schema)
        schema_with_relationships = self._relationship_builder.build(schema)
        tables: dict[str, pd.DataFrame] = {}
        for table in schema_with_relationships.tables:
            tables[table.name.lower()] = self._generate_table(table)
        return tables

    def _generate_table(self, table: TableDefinition) -> pd.DataFrame:
        rows = []
        for index in range(table.rows):
            row = {}
            for column in table.columns:
                row[column.name] = self._generate_value(column, index)
            rows.append(row)
        return pd.DataFrame(rows)

    def _generate_value(self, column: ColumnDefinition, row_index: int) -> Any:
        if column.primary_key:
            return row_index + 1
        if column.default is not None:
            return column.default
        if column.type == "text":
            return self._faker.sentence(nb_words=4)
        if column.type == "integer":
            return int(self._rng.integers(1, 1000))
        if column.type == "decimal":
            return round(float(self._rng.uniform(0, 1000)), 2)
        if column.type == "boolean":
            return bool(self._rng.integers(0, 2))
        if column.type == "date":
            return self._faker.date_between(start_date="-3y", end_date="today")
        if column.type == "timestamp":
            return self._faker.date_time_between(start_date="-3y", end_date="now")
        if column.type == "enum":
            return column.enum_values[0] if column.enum_values else "Unknown"
        if column.type == "currency":
            return round(float(self._rng.uniform(1, 5000)), 2)
        if column.type == "email":
            return self._faker.email()
        if column.type == "phone":
            return self._faker.phone_number()
        if column.type == "address":
            return self._faker.address().replace("\n", ", ")
        if column.type == "country":
            return self._faker.country()
        if column.type == "uuid":
            return self._faker.uuid4()
        return self._faker.word()

    def build_challenge(
        self, tables: dict[str, pd.DataFrame], schema_name: str = "Custom Schema"
    ) -> ChallengePack:
        return ChallengePack(
            title=f"{schema_name} Analysis",
            business_story="A custom schema was generated for exploratory analysis and practice.",
            business_problem="Use the generated tables to explore structure, relationships, and analytical opportunities.",
            difficulty="Intermediate",
            recommended_tools=["SQL", "Python", "Power BI"],
            dashboard_requirements=["Schema overview"],
            sql_questions=[
                "Identify the primary and foreign key relationships in the schema."
            ],
            excel_questions=["Summarize the generated tables."],
            python_questions=["Profile the generated dataset."],
            powerbi_tasks=["Build a dashboard from the custom schema."],
            tableau_tasks=["Visualize key entities."],
            kpis=["Row Count", "Table Count", "Relationship Count"],
            deliverables=["Schema export", "Data export"],
            success_criteria=["Schema validates", "Data exports successfully"],
            estimated_completion_time="3–4 hours",
            machine_learning_ideas=["Synthetic clustering"],
            dataset_metadata={"schema_name": schema_name, "table_count": len(tables)},
            scenario="none",
            quality={},
        )

    def export(
        self, tables: dict[str, pd.DataFrame], schema_name: str = "Custom Schema"
    ) -> Any:
        challenge = self.build_challenge(tables, schema_name)
        return ExportService().export(
            tables, dataset_name=schema_name, challenge_pack=challenge
        )
