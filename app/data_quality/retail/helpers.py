"""Shared safe transformations for retail quality rules."""

import numpy as np
import pandas as pd

from app.utils.retail_metrics import recalculate_retail_totals


class RetailQualityHelper:
    """Provide common table selection and metric recalculation logic."""

    @staticmethod
    def affected_count(total: int, percentage: float) -> int:
        """Return a non-zero count for non-zero percentages and non-empty tables."""
        if total == 0 or percentage <= 0:
            return 0
        return min(total, max(1, round(total * percentage / 100)))

    @staticmethod
    def random_indexes(
        dataframe: pd.DataFrame, percentage: float, random: np.random.Generator
    ) -> pd.Index:
        """Select an approximate percentage of existing DataFrame indices."""
        count = RetailQualityHelper.affected_count(len(dataframe), percentage)
        if count == 0:
            return pd.Index([])
        positions = random.choice(len(dataframe), size=count, replace=False)
        return dataframe.index.take(positions)

    @staticmethod
    def recalculate(dataset: dict[str, pd.DataFrame]) -> None:
        """Recalculate sales and order totals after retail-measure changes when the retail tables exist."""
        if {"orders", "order_items"}.issubset(dataset):
            recalculate_retail_totals(dataset)
