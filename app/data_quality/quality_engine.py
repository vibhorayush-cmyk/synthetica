"""Orchestration for configured data quality rules."""

from collections.abc import Mapping

import numpy as np
import pandas as pd

from app.data_quality.registry import QualityRegistry


class QualityEngine:
    """Apply named quality rules without coupling to an industry schema."""

    def __init__(self, registry: QualityRegistry, seed: int | None = None) -> None:
        self._registry = registry
        self._random = np.random.default_rng(seed)

    def apply(
        self,
        dataset: dict[str, pd.DataFrame],
        quality: Mapping[str, float],
    ) -> dict[str, pd.DataFrame]:
        """Apply enabled rules to a copied dataset in registry-independent order."""
        self._validate_quality(quality)
        enabled_rules = [
            (name, percentage) for name, percentage in quality.items() if percentage > 0
        ]
        if not enabled_rules:
            return dataset

        updated = {
            name: dataframe.copy(deep=True) for name, dataframe in dataset.items()
        }
        for name, percentage in enabled_rules:
            updated = self._registry.get(name).apply(updated, percentage, self._random)
        return updated

    @staticmethod
    def _validate_quality(quality: Mapping[str, float]) -> None:
        for name, percentage in quality.items():
            if not 0 <= percentage <= 100:
                raise ValueError(f"{name} must be between 0 and 100")
