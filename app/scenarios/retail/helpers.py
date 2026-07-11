"""Shared, relationship-safe transformations for retail scenarios."""

import math

import numpy as np
import pandas as pd

from app.utils.retail_metrics import recalculate_retail_totals


class RetailScenarioHelper:
    """Centralize DataFrame transformations used across retail scenarios."""

    @staticmethod
    def clone(dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """Copy tables so a scenario does not mutate the clean baseline."""
        RetailScenarioHelper.validate(dataset)
        return {name: table.copy(deep=True) for name, table in dataset.items()}

    @staticmethod
    def product_ids_for_categories(
        dataset: dict[str, pd.DataFrame], categories: set[str]
    ) -> set[int]:
        """Return IDs of products in the requested categories."""
        products = dataset["products"]
        return set(
            products.loc[products["Category"].isin(categories), "ProductID"].astype(int)
        )

    @staticmethod
    def item_mask_for_products(
        dataset: dict[str, pd.DataFrame], product_ids: set[int]
    ) -> pd.Series:
        """Return an order-item mask for valid selected product IDs."""
        return dataset["order_items"]["ProductID"].isin(product_ids)

    @staticmethod
    def update_items(
        dataset: dict[str, pd.DataFrame],
        mask: pd.Series,
        quantity_multiplier: float = 1.0,
        discount_increase: float = 0.0,
        price_multiplier: float = 1.0,
    ) -> None:
        """Adjust item measures and recalculate sales amounts in place."""
        items = dataset["order_items"]
        if not mask.any():
            return
        quantities = items.loc[mask, "Quantity"].astype(float) * quantity_multiplier
        items.loc[mask, "Quantity"] = np.maximum(1, np.ceil(quantities)).astype(int)
        prices = items.loc[mask, "UnitPrice"].astype(float) * price_multiplier
        items.loc[mask, "UnitPrice"] = np.round(prices, 2)
        discounts = items.loc[mask, "Discount"].astype(float) + discount_increase
        items.loc[mask, "Discount"] = np.round(np.clip(discounts, 0, 0.90), 2)
        RetailScenarioHelper.recalculate_sales(dataset)

    @staticmethod
    def recalculate_sales(dataset: dict[str, pd.DataFrame]) -> None:
        """Recalculate every sales amount after a scenario transformation."""
        recalculate_retail_totals(dataset)

    @staticmethod
    def set_orders_online(
        dataset: dict[str, pd.DataFrame], order_ids: set[int]
    ) -> None:
        """Mark supplied existing orders as online without changing their IDs."""
        orders = dataset["orders"]
        orders.loc[orders["OrderID"].isin(order_ids), "OrderChannel"] = "Online"

    @staticmethod
    def reassign_to_low_cost_products(dataset: dict[str, pd.DataFrame]) -> None:
        """Replace luxury item products with existing low-cost product IDs."""
        products = dataset["products"]
        items = dataset["order_items"]
        low_cost_ids = products.nsmallest(
            max(1, math.ceil(len(products) * 0.3)), "SellingPrice"
        )["ProductID"].to_numpy()
        expensive_ids = set(
            products.nlargest(max(1, math.ceil(len(products) * 0.3)), "SellingPrice")[
                "ProductID"
            ].astype(int)
        )
        mask = items["ProductID"].isin(expensive_ids)
        if not mask.any():
            return
        replacement_ids = np.resize(low_cost_ids, int(mask.sum()))
        items.loc[mask, "ProductID"] = replacement_ids
        price_lookup = products.set_index("ProductID")["SellingPrice"]
        items.loc[mask, "UnitPrice"] = items.loc[mask, "ProductID"].map(price_lookup)

    @staticmethod
    def validate(dataset: dict[str, pd.DataFrame]) -> None:
        """Validate the tables required for relationship-safe retail scenarios."""
        required = {"customers", "products", "stores", "orders", "order_items"}
        missing = required.difference(dataset)
        if missing:
            raise ValueError(f"retail dataset is missing tables: {sorted(missing)}")
