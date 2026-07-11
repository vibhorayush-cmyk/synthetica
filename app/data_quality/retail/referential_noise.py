"""Referential-noise injection for ETL practice."""

import numpy as np
import pandas as pd

from app.data_quality.base import BaseQualityRule
from app.data_quality.retail.helpers import RetailQualityHelper


class ReferentialNoiseRule(BaseQualityRule):
    """Introduce a small optional percentage of invalid foreign-key values."""

    name = "referential_noise"

    def apply(
        self,
        dataset: dict[str, pd.DataFrame],
        percentage: float = 0,
        random: np.random.Generator | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Replace selected foreign keys with values outside parent ID ranges."""
        random = self.random_or_default(random)
        self._inject_noise(dataset.get("orders"), "CustomerID", percentage, random)
        self._inject_noise(dataset.get("orders"), "StoreID", percentage, random)
        self._inject_noise(dataset.get("order_items"), "ProductID", percentage, random)
        return dataset

    @staticmethod
    def _inject_noise(
        dataframe: pd.DataFrame | None,
        column_name: str,
        percentage: float,
        random: np.random.Generator,
    ) -> None:
        if dataframe is None or column_name not in dataframe:
            return
        indexes = RetailQualityHelper.random_indexes(dataframe, percentage, random)
        if len(indexes) == 0:
            return
        base = int(dataframe[column_name].max()) + 1_000_000
        dataframe.loc[indexes, column_name] = base + np.arange(len(indexes))
