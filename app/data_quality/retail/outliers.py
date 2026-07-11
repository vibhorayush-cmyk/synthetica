"""Outlier injection for retail datasets."""

import numpy as np
import pandas as pd

from app.data_quality.base import BaseQualityRule
from app.data_quality.retail.helpers import RetailQualityHelper


class OutliersRule(BaseQualityRule):
    """Inject extreme but structurally valid retail values."""

    name = "outliers"

    def apply(
        self,
        dataset: dict[str, pd.DataFrame],
        percentage: float = 0,
        random: np.random.Generator | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Create high sales, negative profits, extreme quantities and discounts."""
        random = self.random_or_default(random)
        items = dataset.get("order_items")
        customers = dataset.get("customers")
        if items is not None and not items.empty:
            indexes = RetailQualityHelper.random_indexes(items, percentage, random)
            items.loc[indexes, "Quantity"] = 1_000
            items.loc[indexes, "Discount"] = 0.95
            items.loc[indexes, "UnitPrice"] = items.loc[indexes, "UnitPrice"] * 100
            items.loc[indexes, "Profit"] = -abs(
                items.loc[indexes, "UnitPrice"].astype(float)
            )
        if customers is not None and not customers.empty and "Age" in customers:
            indexes = RetailQualityHelper.random_indexes(customers, percentage, random)
            customers.loc[indexes, "Age"] = 120
        RetailQualityHelper.recalculate(dataset)
        return dataset
