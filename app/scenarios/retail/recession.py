"""Recession retail scenario."""

import pandas as pd

from app.scenarios.base import BaseScenario
from app.scenarios.retail.helpers import RetailScenarioHelper


class RecessionScenario(BaseScenario):
    """Shift demand toward lower-cost products and reduce order values."""

    name = "recession"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """Apply lower prices, larger discounts, and low-cost product substitution."""
        updated = RetailScenarioHelper.clone(dataset)
        RetailScenarioHelper.reassign_to_low_cost_products(updated)
        all_items = pd.Series(True, index=updated["order_items"].index)
        RetailScenarioHelper.update_items(
            updated,
            all_items,
            discount_increase=0.10,
            price_multiplier=0.75,
        )
        return updated
