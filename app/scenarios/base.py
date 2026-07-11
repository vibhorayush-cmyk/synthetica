"""Industry-agnostic scenario contract."""

from abc import ABC, abstractmethod

import pandas as pd


class BaseScenario(ABC):
    """Apply a business event to a generated dataset."""

    name: str

    @abstractmethod
    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """Return a dataset modified for this scenario."""
