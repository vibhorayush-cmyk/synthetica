"""Customer table generator."""

import pandas as pd

from app.generators.retail.context import GenerationContext


_LOCATIONS = (
    ("New York", "United States"),
    ("London", "United Kingdom"),
    ("Toronto", "Canada"),
    ("Sydney", "Australia"),
    ("Mumbai", "India"),
    ("Berlin", "Germany"),
)


class CustomersGenerator:
    """Generate realistic retail customer records."""

    id_start = 100_000

    def __init__(self, context: GenerationContext) -> None:
        self._context = context

    def generate(self, count: int) -> pd.DataFrame:
        """Return ``count`` customers with stable, sequential IDs."""
        self._validate_count(count)
        location_indexes = self._context.random.integers(0, len(_LOCATIONS), count)
        locations = [_LOCATIONS[index] for index in location_indexes]
        names = [self._context.faker.name() for _ in range(count)]

        return pd.DataFrame(
            {
                "CustomerID": range(self.id_start, self.id_start + count),
                "Name": names,
                "Email": [
                    f"customer{customer_id}@example.com"
                    for customer_id in range(self.id_start, self.id_start + count)
                ],
                "Phone": [self._context.faker.phone_number() for _ in range(count)],
                "Gender": self._context.random.choice(
                    ["Female", "Male", "Non-binary"], size=count
                ),
                "Age": self._context.random.integers(18, 81, size=count),
                "City": [location[0] for location in locations],
                "Country": [location[1] for location in locations],
                "PostalCode": [self._context.faker.postcode() for _ in range(count)],
            }
        )

    @staticmethod
    def _validate_count(count: int) -> None:
        if count < 1:
            raise ValueError("count must be at least 1")
