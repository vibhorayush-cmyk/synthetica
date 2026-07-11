"""README generation for exported datasets."""

from datetime import datetime
from collections.abc import Mapping

import pandas as pd


class ReadmeGenerator:
    """Create self-contained dataset documentation."""

    def generate(
        self,
        dataset_name: str,
        generated_at: datetime,
        tables: dict[str, pd.DataFrame],
        quality_summary: Mapping[str, float] | None = None,
        challenge_title: str | None = None,
    ) -> str:
        """Return Markdown documentation for an exported dataset."""
        row_counts = "\n".join(
            f"- {table_name}: {len(dataframe):,}"
            for table_name, dataframe in tables.items()
        )
        quality_lines = self._quality_lines(quality_summary)
        return f"""# {dataset_name}

## Dataset Name

{dataset_name}

## Generated Time

{generated_at.strftime("%Y-%m-%d %H:%M:%S")}

## Row Counts

{row_counts}

## Data Quality Summary

{quality_lines}

## Learning Pack

{self._learning_pack_text(challenge_title)}

## Relationship Diagram

```text
Customers (CustomerID) 1 --- * Orders (CustomerID)
Stores (StoreID)       1 --- * Orders (StoreID)
Orders (OrderID)       1 --- * OrderItems (OrderID)
Products (ProductID)   1 --- * OrderItems (ProductID)
```

## Suggested Power BI Model

Use `OrderItems` as the primary sales fact table. Connect it to `Orders` on
`OrderID`; connect `Orders` to the `Customers` and `Stores` dimensions; and
connect `OrderItems` to the `Products` dimension. Use single-direction,
one-to-many relationships from each dimension toward the fact table.
"""

    @staticmethod
    def _quality_lines(quality_summary: Mapping[str, float] | None) -> str:
        if not quality_summary:
            return "No data quality issues were requested."
        return "\n".join(
            f"- {name.replace('_', ' ').title()}: {percentage:g}%"
            for name, percentage in quality_summary.items()
        )

    @staticmethod
    def _learning_pack_text(challenge_title: str | None) -> str:
        if not challenge_title:
            return "No challenge pack was requested for this export."
        return (
            f"`{challenge_title}` is included in `challenge.md` and `challenge.pdf`. "
            "Use `requirements.md` and `dataset_overview.md` to plan the work."
        )
