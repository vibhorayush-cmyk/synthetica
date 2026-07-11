"""Unit tests for the retail dataset generator."""

from datetime import date, timedelta

import numpy as np

from app.generators.retail import RetailDatasetGenerator, RetailGenerationConfig


def test_generates_expected_table_counts_and_id_starts() -> None:
    """Each generator returns the requested records and starting IDs."""
    tables = _generate_tables()

    assert len(tables["customers"]) == 10
    assert len(tables["products"]) == 8
    assert len(tables["stores"]) == 3
    assert len(tables["orders"]) == 20
    assert len(tables["order_items"]) == 40
    assert tables["customers"].iloc[0]["CustomerID"] == 100_000
    assert tables["products"].iloc[0]["ProductID"] == 1_000
    assert tables["stores"].iloc[0]["StoreID"] == 100
    assert tables["orders"].iloc[0]["OrderID"] == 500_000


def test_foreign_keys_refer_to_generated_parent_records() -> None:
    """Orders and order items maintain all specified relationships."""
    tables = _generate_tables()

    assert set(tables["orders"]["CustomerID"]).issubset(
        set(tables["customers"]["CustomerID"])
    )
    assert set(tables["orders"]["StoreID"]).issubset(set(tables["stores"]["StoreID"]))
    assert set(tables["order_items"]["OrderID"]).issubset(
        set(tables["orders"]["OrderID"])
    )
    assert set(tables["order_items"]["ProductID"]).issubset(
        set(tables["products"]["ProductID"])
    )


def test_order_item_amounts_and_order_dates_are_valid() -> None:
    """Line totals are calculated correctly and dates stay within three years."""
    tables = _generate_tables()
    items = tables["order_items"]
    expected_sales = np.round(
        items["Quantity"] * items["UnitPrice"] * (1 - items["Discount"]), 2
    )
    oldest_valid_date = date.today() - timedelta(days=3 * 365)

    assert np.allclose(items["SalesAmount"], expected_sales)
    assert tables["orders"]["OrderDate"].between(oldest_valid_date, date.today()).all()


def _generate_tables():
    config = RetailGenerationConfig(
        customers=10,
        products=8,
        stores=3,
        orders=20,
        order_items=40,
        seed=7,
    )
    return RetailDatasetGenerator(config).generate()
