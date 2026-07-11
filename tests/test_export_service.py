"""Unit tests for the dataset export service."""

from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from app.exporters import ExportService
from app.exporters.data_dictionary import DataDictionaryGenerator


def test_export_service_creates_retail_bundle(tmp_path: Path) -> None:
    """The service writes all artifacts and produces a matching ZIP archive."""
    tables = _retail_tables()
    service = ExportService(
        exports_root=tmp_path,
        clock=lambda: datetime(2026, 7, 12, 14, 30, 45),
    )

    result = service.export(tables)

    folder = Path(result.folder_path)
    assert folder.name == "Retail_20260712_143045"
    assert Path(result.zip_path).name == "Retail_20260712_143045.zip"
    assert {path.name for path in folder.iterdir()} == {
        "customers.csv",
        "products.csv",
        "stores.csv",
        "orders.csv",
        "order_items.csv",
        "data_dictionary.xlsx",
        "README.md",
    }
    assert len(result.files) == 7
    assert result.generated_at == datetime(2026, 7, 12, 14, 30, 45)
    readme = (folder / "README.md").read_text(encoding="utf-8")
    assert "## Relationship Diagram" in readme
    assert "## Suggested Power BI Model" in readme

    with ZipFile(result.zip_path) as archive:
        assert set(archive.namelist()) == {
            "Retail_20260712_143045/customers.csv",
            "Retail_20260712_143045/products.csv",
            "Retail_20260712_143045/stores.csv",
            "Retail_20260712_143045/orders.csv",
            "Retail_20260712_143045/order_items.csv",
            "Retail_20260712_143045/data_dictionary.xlsx",
            "Retail_20260712_143045/README.md",
        }


def test_data_dictionary_identifies_retail_keys() -> None:
    """The generated dictionary declares documented primary and foreign keys."""
    dictionary = DataDictionaryGenerator().generate(_retail_tables())

    customer_key = dictionary.loc[
        (dictionary["Table Name"] == "customers")
        & (dictionary["Column Name"] == "CustomerID")
    ].iloc[0]
    order_customer_key = dictionary.loc[
        (dictionary["Table Name"] == "orders")
        & (dictionary["Column Name"] == "CustomerID")
    ].iloc[0]

    assert customer_key["Primary Key"] == "Yes"
    assert order_customer_key["Foreign Key"] == "customers.CustomerID"
    assert list(dictionary.columns) == [
        "Table Name",
        "Column Name",
        "Data Type",
        "Description",
        "Primary Key",
        "Foreign Key",
    ]


def test_export_readme_includes_data_quality_summary(tmp_path: Path) -> None:
    """Export documentation records each configured quality injection rate."""
    result = ExportService(exports_root=tmp_path).export(
        _retail_tables(),
        quality_summary={"missing_values": 5, "duplicates": 2, "outliers": 1},
    )

    readme = (Path(result.folder_path) / "README.md").read_text(encoding="utf-8")
    assert "## Data Quality Summary" in readme
    assert "- Missing Values: 5%" in readme
    assert "- Duplicates: 2%" in readme
    assert "- Outliers: 1%" in readme


def _retail_tables() -> dict[str, pd.DataFrame]:
    return {
        "customers": pd.DataFrame({"CustomerID": [100_000], "Name": ["Ada"]}),
        "products": pd.DataFrame({"ProductID": [1_000], "SellingPrice": [12.5]}),
        "stores": pd.DataFrame({"StoreID": [100], "City": ["Mumbai"]}),
        "orders": pd.DataFrame(
            {"OrderID": [500_000], "CustomerID": [100_000], "StoreID": [100]}
        ),
        "order_items": pd.DataFrame(
            {"OrderID": [500_000], "ProductID": [1_000], "Quantity": [2]}
        ),
    }
