from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PluginMetadata:
    id: str
    name: str
    description: str
    version: str
    status: str = "available"


class BaseIndustryPlugin(ABC):
    """Base contract for all industry plugins."""

    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def version(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def supported_scenarios(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def supported_quality_rules(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def default_templates(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def default_counts(self) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    def generate(self, config: Any, export_service: Any | None = None) -> Any:
        raise NotImplementedError

    @abstractmethod
    def validate(self, config: Any) -> None:
        raise NotImplementedError

    def metadata(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name(),
            "description": self.description(),
            "version": self.version(),
            "status": "available",
        }

    def frontend_metadata(self) -> dict[str, Any]:
        """Return the complete UI contract for this industry plugin."""
        return {
            **self.metadata(),
            "icon": "database",
            "color": "#4f46e5",
            "configuration_fields": [],
            "supported_scenarios": self.supported_scenarios(),
            "supported_templates": self.default_templates(),
            "kpis": [],
            "dashboard_suggestions": [],
            "challenge_types": [],
            "field_layout": [],
            "generation_available": True,
        }
