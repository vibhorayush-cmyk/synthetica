"""Duplicate-record injection for retail datasets."""

import numpy as np
import pandas as pd

from app.data_quality.base import BaseQualityRule
from app.data_quality.retail.helpers import RetailQualityHelper


class DuplicatesRule(BaseQualityRule):
    """Duplicate customer and order attributes while preserving primary keys."""

    name = "duplicates"

    def apply(
        self,
        dataset: dict[str, pd.DataFrame],
        percentage: float = 0,
        random: np.random.Generator | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Append near-duplicate customers and orders with new valid IDs."""
        random = self.random_or_default(random)
        self._duplicate_customers(dataset, percentage, random)
        self._duplicate_orders(dataset, percentage, random)
        RetailQualityHelper.recalculate(dataset)
        return dataset

    @staticmethod
    def _duplicate_customers(
        dataset: dict[str, pd.DataFrame], percentage: float, random: np.random.Generator
    ) -> None:
        customers = dataset.get("customers")
        if customers is None or customers.empty or "CustomerID" not in customers:
            return
        indexes = RetailQualityHelper.random_indexes(customers, percentage, random)
        copies = customers.loc[indexes].copy()
        if copies.empty:
            return
        start_id = int(customers["CustomerID"].max()) + 1
        copies["CustomerID"] = range(start_id, start_id + len(copies))
        dataset["customers"] = pd.concat([customers, copies], ignore_index=True)

    @staticmethod
    def _duplicate_orders(
        dataset: dict[str, pd.DataFrame], percentage: float, random: np.random.Generator
    ) -> None:
        orders = dataset.get("orders")
        items = dataset.get("order_items")
        if orders is None or items is None or orders.empty or "OrderID" not in orders:
            return
        indexes = RetailQualityHelper.random_indexes(orders, percentage, random)
        copies = orders.loc[indexes].copy()
        if copies.empty:
            return
        source_ids = copies["OrderID"].astype(int).to_list()
        start_id = int(orders["OrderID"].max()) + 1
        new_ids = list(range(start_id, start_id + len(copies)))
        copies["OrderID"] = new_ids
        dataset["orders"] = pd.concat([orders, copies], ignore_index=True)
        item_copies = items.loc[items["OrderID"].isin(source_ids)].copy()
        id_mapping = dict(zip(source_ids, new_ids, strict=True))
        item_copies["OrderID"] = item_copies["OrderID"].map(id_mapping)
        dataset["order_items"] = pd.concat([items, item_copies], ignore_index=True)
