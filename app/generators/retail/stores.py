"""Store table generator."""

import pandas as pd

from app.generators.retail.context import GenerationContext


_STORE_LOCATIONS = (
    ("New York", "New York", "United States"),
    ("Austin", "Texas", "United States"),
    ("London", "England", "United Kingdom"),
    ("Toronto", "Ontario", "Canada"),
    ("Sydney", "New South Wales", "Australia"),
    ("Mumbai", "Maharashtra", "India"),
)


class StoresGenerator:
    """Generate store locations."""

    id_start = 100

    def __init__(self, context: GenerationContext) -> None:
        self._context = context

    def generate(self, count: int) -> pd.DataFrame:
        """Return ``count`` stores with stable, sequential IDs."""
        if count < 1:
            raise ValueError("count must be at least 1")

        indexes = self._context.random.integers(0, len(_STORE_LOCATIONS), count)
        locations = [_STORE_LOCATIONS[index] for index in indexes]
        return pd.DataFrame(
            {
                "StoreID": range(self.id_start, self.id_start + count),
                "StoreName": [f"{location[0]} Store" for location in locations],
                "City": [location[0] for location in locations],
                "State": [location[1] for location in locations],
                "Country": [location[2] for location in locations],
                "PostalCode": [self._context.faker.postcode() for _ in range(count)],
            }
        )
