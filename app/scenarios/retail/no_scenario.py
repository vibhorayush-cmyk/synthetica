"""No-op retail scenario."""

import pandas as pd

from app.scenarios.base import BaseScenario


class NoScenario(BaseScenario):
    """Keep the generated baseline dataset unchanged."""

    name = "none"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """Return the original dataset without copying or modifying it."""
        return dataset
