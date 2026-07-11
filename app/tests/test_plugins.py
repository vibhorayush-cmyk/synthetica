import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.plugins.interfaces import PluginGenerationConfig
from app.plugins.loader import discover_plugins
from app.plugins.registry import PluginRegistry
from app.plugins.retail.plugin import RetailPlugin


def test_plugin_registration_and_lookup() -> None:
    registry = PluginRegistry()
    registry.clear()
    plugin = RetailPlugin()

    registry.register(plugin)

    assert registry.get("retail") is plugin
    assert "retail" in registry.list_ids()


def test_plugin_discovery_finds_retail_plugin() -> None:
    discovered = discover_plugins()

    assert any(plugin.id == "retail" for plugin in discovered)


def test_unknown_plugin_raises_value_error() -> None:
    registry = PluginRegistry()
    registry.clear()

    with pytest.raises(ValueError, match="Unknown industry plugin"):
        registry.get("banking")


def test_retail_plugin_generates_dataset() -> None:
    plugin = RetailPlugin()
    config = PluginGenerationConfig(
        industry="retail",
        scenario="none",
        customers=50,
        products=10,
        stores=3,
        orders=100,
        export_type="zip",
        quality={
            "missing_values": 1.0,
            "duplicates": 0.0,
            "outliers": 0.0,
            "invalid_formats": 0.0,
            "referential_noise": 0.0,
        },
    )

    result = plugin.generate(config)

    assert result.tables
    assert result.export.zip_path.endswith(".zip")
    assert result.challenge.title


def test_industries_endpoint_lists_available_and_coming_soon() -> None:
    client = TestClient(app)
    response = client.get("/industries")

    assert response.status_code == 200
    payload = response.json()

    available = next(item for item in payload if item["id"] == "retail")
    assert available["status"] == "available"

    banking = next(item for item in payload if item["id"] == "banking")
    assert banking["status"] == "available"
