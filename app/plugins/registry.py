from __future__ import annotations

from app.plugins.base import BaseIndustryPlugin
from app.plugins.loader import discover_plugins


class PluginRegistry:
    """Registry for available industry plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, BaseIndustryPlugin] = {}

    def register(self, plugin: BaseIndustryPlugin) -> None:
        self._plugins[plugin.id] = plugin

    def get(self, plugin_id: str) -> BaseIndustryPlugin:
        if plugin_id not in self._plugins:
            raise ValueError(f"Unknown industry plugin: {plugin_id}")
        return self._plugins[plugin_id]

    def list_ids(self) -> list[str]:
        return sorted(self._plugins)

    def clear(self) -> None:
        self._plugins.clear()

    def list_metadata(self) -> list[dict[str, object]]:
        return [self._plugins[plugin_id].metadata() for plugin_id in self.list_ids()]

    def frontend_metadata(self, plugin_id: str) -> dict[str, object]:
        """Return the complete UI contract for a registered plugin."""
        return self.get(plugin_id).frontend_metadata()

    def list_frontend_metadata(self) -> list[dict[str, object]]:
        """Return frontend contracts for all registered plugins."""
        return [self._plugins[plugin_id].frontend_metadata() for plugin_id in self.list_ids()]


def create_default_plugin_registry() -> PluginRegistry:
    """Create a registry populated with discovered plugins."""
    registry = PluginRegistry()
    for plugin in discover_plugins():
        registry.register(plugin)
    return registry
