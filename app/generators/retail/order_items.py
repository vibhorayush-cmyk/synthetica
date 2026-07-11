"""Order-item table generator."""

import numpy as np
import pandas as pd

from app.generators.retail.context import GenerationContext


class OrderItemsGenerator:
    """Generate individual line items linked to orders and products."""

    def __init__(self, context: GenerationContext) -> None:
        self._context = context

    def generate(
        self, count: int, orders: pd.DataFrame, products: pd.DataFrame
    ) -> pd.DataFrame:
        """Return line items with prices derived from their products."""
        if count < 1:
            raise ValueError("count must be at least 1")
        self._validate_dependencies(orders, products)

        selected_products = self._context.random.choice(
            products[["ProductID", "SellingPrice"]].to_records(index=False), size=count
        )
        quantities = self._context.random.integers(1, 6, size=count)
        discounts = self._context.random.choice(
            np.array([0.00, 0.05, 0.10, 0.15, 0.20]), size=count
        )
        unit_prices = np.round(selected_products["SellingPrice"].astype(float), 2)
        sales_amounts = np.round(quantities * unit_prices * (1 - discounts), 2)

        return pd.DataFrame(
            {
                "OrderID": self._context.random.choice(
                    orders["OrderID"].to_numpy(), size=count
                ),
                "ProductID": selected_products["ProductID"],
                "Quantity": quantities,
                "UnitPrice": unit_prices,
                "Discount": discounts,
                "SalesAmount": sales_amounts,
                "IsReturned": self._context.random.choice(
                    [False, True], size=count, p=[0.95, 0.05]
                ),
            }
        )

    @staticmethod
    def _validate_dependencies(orders: pd.DataFrame, products: pd.DataFrame) -> None:
        if orders.empty or "OrderID" not in orders:
            raise ValueError("orders must contain at least one OrderID")
        required_columns = {"ProductID", "SellingPrice"}
        if products.empty or not required_columns.issubset(products.columns):
            raise ValueError("products must contain ProductID and SellingPrice")
