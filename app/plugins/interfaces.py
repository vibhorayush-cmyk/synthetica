from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class PluginGenerationConfig:
    industry: str
    scenario: str = "none"
    customers: int = 1
    products: int = 1
    stores: int = 1
    orders: int = 1
    export_type: str = "zip"
    quality: dict[str, float] = field(default_factory=dict)
    configuration: dict[str, int] = field(default_factory=dict)

    def get_count(self, key: str, default: int | None = None) -> int:
        """Resolve plugin configuration first, preserving legacy request fields."""
        if key in self.configuration:
            return self.configuration[key]
        legacy_value = getattr(self, key, None)
        if legacy_value is not None:
            return legacy_value
        if default is not None:
            return default
        raise ValueError(f"missing configuration value: {key}")


@dataclass(frozen=True, slots=True)
class PluginGenerationResult:
    tables: dict[str, Any]
    export: Any
    scenario: str
    quality: dict[str, float]
    challenge: Any
