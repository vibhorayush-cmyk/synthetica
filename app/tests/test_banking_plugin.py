from __future__ import annotations


from app.plugins.interfaces import PluginGenerationConfig
from app.plugins.loader import discover_plugins
from app.plugins.registry import PluginRegistry
from app.plugins.banking.plugin import BankingPlugin


def test_banking_plugin_registration_and_discovery() -> None:
    registry = PluginRegistry()
    registry.clear()
    plugin = BankingPlugin()
    registry.register(plugin)

    assert registry.get("banking") is plugin
    assert "banking" in registry.list_ids()

    discovered = discover_plugins()
    assert any(item.id == "banking" for item in discovered)


def test_banking_plugin_generates_expected_tables_and_relationships() -> None:
    plugin = BankingPlugin()
    config = PluginGenerationConfig(
        industry="banking",
        scenario="none",
        customers=50,
        products=1,
        stores=1,
        orders=1,
        export_type="zip",
        quality={
            "missing_values": 0.0,
            "duplicates": 0.0,
            "outliers": 0.0,
            "invalid_formats": 0.0,
            "referential_noise": 0.0,
        },
    )

    result = plugin.generate(config)

    assert set(result.tables) == {
        "customers",
        "accounts",
        "branches",
        "transactions",
        "loans",
        "credit_cards",
        "payments",
    }
    assert (
        result.tables["accounts"]["CustomerID"]
        .isin(result.tables["customers"]["CustomerID"])
        .all()
    )
    assert (
        result.tables["accounts"]["BranchID"]
        .isin(result.tables["branches"]["BranchID"])
        .all()
    )
    assert (
        result.tables["transactions"]["AccountID"]
        .isin(result.tables["accounts"]["AccountID"])
        .all()
    )
    assert (
        result.tables["loans"]["CustomerID"]
        .isin(result.tables["customers"]["CustomerID"])
        .all()
    )
    assert (
        result.tables["credit_cards"]["CustomerID"]
        .isin(result.tables["customers"]["CustomerID"])
        .all()
    )
    assert (
        result.tables["payments"]["TransactionID"]
        .isin(result.tables["transactions"]["TransactionID"])
        .all()
    )


def test_banking_plugin_scenarios_and_templates() -> None:
    plugin = BankingPlugin()

    assert plugin.supported_scenarios() == [
        "none",
        "fraud_spike",
        "interest_rate_hike",
        "loan_default_wave",
        "holiday_spending",
    ]
    assert plugin.default_templates()[0]["name"] == "Banking Beginner"
    assert plugin.metadata()["version"] == "1.0"


def test_banking_plugin_challenge_generation_and_export() -> None:
    plugin = BankingPlugin()
    config = PluginGenerationConfig(
        industry="banking",
        scenario="fraud_spike",
        customers=30,
        products=1,
        stores=1,
        orders=1,
        export_type="zip",
        quality={
            "missing_values": 2.5,
            "duplicates": 1.0,
            "outliers": 0.0,
            "invalid_formats": 0.0,
            "referential_noise": 0.0,
        },
    )

    result = plugin.generate(config)

    assert result.challenge.title
    assert result.export.zip_path.endswith(".zip")
    assert result.scenario == "fraud_spike"
