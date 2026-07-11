"""Product table generator."""

import numpy as np
import pandas as pd

from app.generators.retail.context import GenerationContext


_PRODUCT_CATALOG = {
    "Electronics": ("Vertex", "Lumina", "Apex"),
    "Toys": ("Playcraft", "BrightMinds", "WonderWorks"),
    "Gifts": ("Keepsake", "Gifted", "Ribbon & Co."),
    "Fashion": ("Northstar", "Urban Thread", "Everlane"),
    "Decorations": ("Hearth & Home", "Casa", "Oakline"),
    "Clothing": ("Threadline", "Mode", "Daywear"),
    "Outdoor": ("Summit", "Trailhead", "Campside"),
    "Ice Cream": ("Creamery", "Frost & Co.", "Scoop"),
    "Beverages": ("Refresh", "Orchard", "Spark"),
    "Luxury": ("Atelier", "Prestige", "Gilded"),
}


class ProductsGenerator:
    """Generate retail products and financially consistent prices."""

    id_start = 1_000

    def __init__(self, context: GenerationContext) -> None:
        self._context = context

    def generate(self, count: int) -> pd.DataFrame:
        """Return ``count`` products with cost and selling prices."""
        if count < 1:
            raise ValueError("count must be at least 1")

        categories = self._context.random.choice(list(_PRODUCT_CATALOG), size=count)
        cost_prices = np.round(self._context.random.uniform(5, 500, size=count), 2)
        margins = self._context.random.uniform(1.15, 1.8, size=count)
        selling_prices = np.round(cost_prices * margins, 2)

        return pd.DataFrame(
            {
                "ProductID": range(self.id_start, self.id_start + count),
                "Category": categories,
                "Brand": [
                    self._context.random.choice(_PRODUCT_CATALOG[category])
                    for category in categories
                ],
                "CostPrice": cost_prices,
                "SellingPrice": selling_prices,
                "Currency": "USD",
            }
        )
