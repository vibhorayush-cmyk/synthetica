"""Order table generator."""

from datetime import date, timedelta

import pandas as pd

from app.generators.retail.context import GenerationContext


class OrdersGenerator:
    """Generate orders linked to existing customers and stores."""

    id_start = 500_000

    def __init__(self, context: GenerationContext) -> None:
        self._context = context

    def generate(
        self, count: int, customers: pd.DataFrame, stores: pd.DataFrame
    ) -> pd.DataFrame:
        """Return orders whose foreign keys point to supplied tables."""
        if count < 1:
            raise ValueError("count must be at least 1")
        self._validate_dependencies(customers, stores)
        start_date = date.today() - timedelta(days=3 * 365)
        day_offsets = self._context.random.integers(0, 3 * 365 + 1, size=count)

        return pd.DataFrame(
            {
                "OrderID": range(self.id_start, self.id_start + count),
                "CustomerID": self._context.random.choice(
                    customers["CustomerID"].to_numpy(), size=count
                ),
                "StoreID": self._context.random.choice(
                    stores["StoreID"].to_numpy(), size=count
                ),
                "OrderDate": [
                    start_date + timedelta(days=int(offset)) for offset in day_offsets
                ],
                "PaymentMethod": self._context.random.choice(
                    ["Credit Card", "Debit Card", "Cash", "Digital Wallet"],
                    size=count,
                ),
                "OrderChannel": self._context.random.choice(
                    ["In Store", "Online"], size=count, p=[0.65, 0.35]
                ),
                "OrderTotal": 0.0,
            }
        )

    @staticmethod
    def _validate_dependencies(customers: pd.DataFrame, stores: pd.DataFrame) -> None:
        if customers.empty or "CustomerID" not in customers:
            raise ValueError("customers must contain at least one CustomerID")
        if stores.empty or "StoreID" not in stores:
            raise ValueError("stores must contain at least one StoreID")
