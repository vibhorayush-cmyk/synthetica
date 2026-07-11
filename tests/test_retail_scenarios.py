"""Unit tests for relationship-safe retail scenarios."""

from datetime import date

import pandas as pd
from pandas.testing import assert_frame_equal

from app.scenarios.retail.black_friday import BlackFridayScenario
from app.scenarios.retail.christmas import ChristmasScenario
from app.scenarios.retail.no_scenario import NoScenario
from app.scenarios.retail.recession import RecessionScenario


def test_black_friday_increases_electronics_sales_and_online_orders() -> None:
    """Black Friday raises sales for existing electronics items."""
    baseline = _baseline_dataset()
    updated = BlackFridayScenario().apply(baseline)

    electronic_sales = (
        updated["order_items"]
        .loc[updated["order_items"]["ProductID"] == 1_000, "SalesAmount"]
        .sum()
    )
    baseline_sales = (
        baseline["order_items"]
        .loc[baseline["order_items"]["ProductID"] == 1_000, "SalesAmount"]
        .sum()
    )

    assert electronic_sales > baseline_sales
    assert updated["orders"].loc[0, "OrderChannel"] == "Online"
    _assert_foreign_keys(updated)


def test_recession_lowers_average_order_item_value() -> None:
    """Recession decreases average order-item sales through price pressure."""
    baseline = _baseline_dataset()
    updated = RecessionScenario().apply(baseline)

    assert (
        updated["order_items"]["SalesAmount"].mean()
        < baseline["order_items"]["SalesAmount"].mean()
    )
    _assert_foreign_keys(updated)


def test_christmas_increases_toy_sales_and_marks_late_returns() -> None:
    """Christmas demand raises toy sales and late-December returns."""
    baseline = _baseline_dataset()
    updated = ChristmasScenario().apply(baseline)

    toy_sales = (
        updated["order_items"]
        .loc[updated["order_items"]["ProductID"] == 1_001, "SalesAmount"]
        .sum()
    )
    baseline_toy_sales = (
        baseline["order_items"]
        .loc[baseline["order_items"]["ProductID"] == 1_001, "SalesAmount"]
        .sum()
    )

    assert toy_sales > baseline_toy_sales
    assert updated["order_items"].loc[1, "IsReturned"]
    _assert_foreign_keys(updated)


def test_no_scenario_leaves_dataset_unchanged() -> None:
    """The no-op scenario preserves every baseline table exactly."""
    baseline = _baseline_dataset()
    unchanged = NoScenario().apply(baseline)

    assert unchanged is baseline
    for table_name, dataframe in baseline.items():
        assert_frame_equal(unchanged[table_name], dataframe)


def _assert_foreign_keys(dataset: dict[str, pd.DataFrame]) -> None:
    assert set(dataset["orders"]["CustomerID"]).issubset(
        set(dataset["customers"]["CustomerID"])
    )
    assert set(dataset["orders"]["StoreID"]).issubset(set(dataset["stores"]["StoreID"]))
    assert set(dataset["order_items"]["OrderID"]).issubset(
        set(dataset["orders"]["OrderID"])
    )
    assert set(dataset["order_items"]["ProductID"]).issubset(
        set(dataset["products"]["ProductID"])
    )


def _baseline_dataset() -> dict[str, pd.DataFrame]:
    return {
        "customers": pd.DataFrame({"CustomerID": [100_000]}),
        "products": pd.DataFrame(
            {
                "ProductID": [1_000, 1_001, 1_002, 1_003],
                "Category": ["Electronics", "Toys", "Luxury", "Beverages"],
                "SellingPrice": [100.0, 40.0, 1_000.0, 10.0],
            }
        ),
        "stores": pd.DataFrame({"StoreID": [100]}),
        "orders": pd.DataFrame(
            {
                "OrderID": [500_000, 500_001, 500_002, 500_003],
                "CustomerID": [100_000] * 4,
                "StoreID": [100] * 4,
                "OrderDate": [
                    date(2025, 11, 28),
                    date(2025, 12, 27),
                    date(2025, 12, 20),
                    date(2025, 7, 1),
                ],
                "OrderChannel": ["In Store"] * 4,
                "OrderTotal": [100.0, 40.0, 1_000.0, 10.0],
            }
        ),
        "order_items": pd.DataFrame(
            {
                "OrderID": [500_000, 500_001, 500_002, 500_003],
                "ProductID": [1_000, 1_001, 1_002, 1_003],
                "Quantity": [1, 1, 1, 1],
                "UnitPrice": [100.0, 40.0, 1_000.0, 10.0],
                "Discount": [0.0, 0.0, 0.0, 0.0],
                "SalesAmount": [100.0, 40.0, 1_000.0, 10.0],
                "IsReturned": [False, False, False, False],
            }
        ),
    }
