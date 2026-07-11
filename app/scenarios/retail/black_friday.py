"""Black Friday retail scenario."""

import pandas as pd

from app.scenarios.base import BaseScenario
from app.scenarios.retail.helpers import RetailScenarioHelper


class BlackFridayScenario(BaseScenario):
    """Increase electronics demand, discounts, online orders, and sales."""

    name = "black_friday"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """Apply a Black Friday promotion to existing electronics order items."""
        updated = RetailScenarioHelper.clone(dataset)
        product_ids = RetailScenarioHelper.product_ids_for_categories(
            updated, {"Electronics"}
        )
        mask = RetailScenarioHelper.item_mask_for_products(updated, product_ids)
        RetailScenarioHelper.update_items(
            updated,
            mask,
            quantity_multiplier=1.5,
            discount_increase=0.15,
        )
        RetailScenarioHelper.set_orders_online(
            updated, set(updated["order_items"].loc[mask, "OrderID"].astype(int))
        )
        return updated
