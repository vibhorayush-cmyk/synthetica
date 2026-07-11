"""Retail financial metric calculations shared by transformations."""

import numpy as np
import pandas as pd


def recalculate_retail_totals(dataset: dict[str, pd.DataFrame]) -> None:
    """Recalculate order-item sales and the corresponding order totals."""
    items = dataset["order_items"]
    items["SalesAmount"] = np.round(
        items["Quantity"].astype(float)
        * items["UnitPrice"].astype(float)
        * (1 - items["Discount"].astype(float)),
        2,
    )
    orders = dataset["orders"]
    totals = items.groupby("OrderID")["SalesAmount"].sum()
    orders["OrderTotal"] = np.round(orders["OrderID"].map(totals).fillna(0), 2)
