"""Christmas retail scenario."""

import pandas as pd

from app.scenarios.base import BaseScenario
from app.scenarios.retail.helpers import RetailScenarioHelper


class ChristmasScenario(BaseScenario):
    """Increase seasonal category demand and post-Christmas returns."""

    name = "christmas"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """Apply seasonal demand to existing Christmas-related order items."""
        updated = RetailScenarioHelper.clone(dataset)
        product_ids = RetailScenarioHelper.product_ids_for_categories(
            updated, {"Toys", "Gifts", "Fashion", "Decorations"}
        )
        mask = RetailScenarioHelper.item_mask_for_products(updated, product_ids)
        RetailScenarioHelper.update_items(
            updated,
            mask,
            quantity_multiplier=1.4,
            discount_increase=0.08,
        )
        self._increase_post_christmas_returns(updated)
        return updated

    @staticmethod
    def _increase_post_christmas_returns(dataset: dict[str, pd.DataFrame]) -> None:
        orders = dataset["orders"]
        order_items = dataset["order_items"]
        dates = pd.to_datetime(orders["OrderDate"])
        post_christmas_ids = set(
            orders.loc[(dates.dt.month == 12) & (dates.dt.day > 25), "OrderID"].astype(
                int
            )
        )
        order_items.loc[
            order_items["OrderID"].isin(post_christmas_ids), "IsReturned"
        ] = True
