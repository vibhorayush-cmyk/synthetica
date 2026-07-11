"""Invalid-format injection for retail datasets."""

import numpy as np
import pandas as pd

from app.data_quality.base import BaseQualityRule
from app.data_quality.retail.helpers import RetailQualityHelper


class InvalidFormatsRule(BaseQualityRule):
    """Create malformed values without changing keys or relationships."""

    name = "invalid_formats"

    def apply(
        self,
        dataset: dict[str, pd.DataFrame],
        percentage: float = 0,
        random: np.random.Generator | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Break selected formats across supported retail attributes."""
        random = self.random_or_default(random)
        self._set_invalid_customer_formats(dataset.get("customers"), percentage, random)
        self._set_invalid_store_formats(dataset.get("stores"), percentage, random)
        self._set_invalid_order_dates(dataset.get("orders"), percentage, random)
        self._set_currency_mismatches(dataset.get("products"), percentage, random)
        return dataset

    @staticmethod
    def _set_invalid_customer_formats(
        customers: pd.DataFrame | None, percentage: float, random: np.random.Generator
    ) -> None:
        if customers is None:
            return
        indexes = RetailQualityHelper.random_indexes(customers, percentage, random)
        if "Email" in customers:
            customers.loc[indexes, "Email"] = "not-an-email"
        if "Phone" in customers:
            customers.loc[indexes, "Phone"] = "ABC-INVALID"
        if "PostalCode" in customers:
            customers.loc[indexes, "PostalCode"] = "???"
        if "Country" in customers:
            customers.loc[indexes, "Country"] = "Narnia"

    @staticmethod
    def _set_invalid_store_formats(
        stores: pd.DataFrame | None, percentage: float, random: np.random.Generator
    ) -> None:
        if stores is None:
            return
        indexes = RetailQualityHelper.random_indexes(stores, percentage, random)
        if "PostalCode" in stores:
            stores.loc[indexes, "PostalCode"] = "POST-INVALID"
        if "Country" in stores:
            stores.loc[indexes, "Country"] = "Unknown Territory"

    @staticmethod
    def _set_invalid_order_dates(
        orders: pd.DataFrame | None, percentage: float, random: np.random.Generator
    ) -> None:
        if orders is None or "OrderDate" not in orders:
            return
        indexes = RetailQualityHelper.random_indexes(orders, percentage, random)
        for position, index in enumerate(indexes):
            parsed_date = pd.Timestamp(orders.at[index, "OrderDate"])
            orders.at[index, "OrderDate"] = parsed_date.strftime(
                "%d/%m/%Y" if position % 2 else "%Y.%m.%d"
            )

    @staticmethod
    def _set_currency_mismatches(
        products: pd.DataFrame | None, percentage: float, random: np.random.Generator
    ) -> None:
        if products is None or "Currency" not in products:
            return
        indexes = RetailQualityHelper.random_indexes(products, percentage, random)
        products.loc[indexes, "Currency"] = "ZZZ"
