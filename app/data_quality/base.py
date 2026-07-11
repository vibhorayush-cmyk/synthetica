"""Industry-agnostic data quality rule contract."""

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class BaseQualityRule(ABC):
    """Inject a single type of realistic quality issue into a dataset."""

    name: str

    @abstractmethod
    def apply(
        self,
        dataset: dict[str, pd.DataFrame],
        percentage: float = 0,
        random: np.random.Generator | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Apply this rule and return the modified dataset."""

    @staticmethod
    def random_or_default(random: np.random.Generator | None) -> np.random.Generator:
        """Use an injected generator or create one for direct rule invocation."""
        return random if random is not None else np.random.default_rng()
