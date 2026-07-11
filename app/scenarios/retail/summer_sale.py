"""Summer Sale retail scenario."""

import pandas as pd

from app.scenarios.base import BaseScenario
from app.scenarios.retail.helpers import RetailScenarioHelper


class SummerSaleScenario(BaseScenario):
    """Increase summer-category demand and discount rates."""

    name = "summer_sale"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """Apply a summer promotion to existing seasonal products."""
        updated = RetailScenarioHelper.clone(dataset)
        product_ids = RetailScenarioHelper.product_ids_for_categories(
            updated, {"Clothing", "Outdoor", "Ice Cream", "Beverages"}
        )
        mask = RetailScenarioHelper.item_mask_for_products(updated, product_ids)
        RetailScenarioHelper.update_items(
            updated,
            mask,
            quantity_multiplier=1.3,
            discount_increase=0.20,
        )
        return updated
