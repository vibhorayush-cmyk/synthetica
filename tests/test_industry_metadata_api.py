"""Integration tests for frontend industry plugin metadata."""

from fastapi.testclient import TestClient

from app.main import app


def test_industry_metadata_describes_dynamic_retail_configuration() -> None:
    """Retail metadata contains every contract field needed by the frontend."""
    with TestClient(app) as client:
        response = client.get("/industries/retail")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Retail"
    assert [field["key"] for field in payload["configuration_fields"]] == [
        "customers",
        "products",
        "stores",
        "orders",
    ]
    assert "black_friday" in payload["supported_scenarios"]
    assert payload["kpis"]
    assert payload["field_layout"]


def test_industry_metadata_describes_banking_and_healthcare_fields() -> None:
    """The same contract renders future industry configuration without React changes."""
    with TestClient(app) as client:
        banking = client.get("/industries/banking").json()
        healthcare = client.get("/industries/healthcare").json()

    assert {field["key"] for field in banking["configuration_fields"]} >= {
        "customers",
        "accounts",
        "transactions",
        "loans",
        "branches",
        "credit_cards",
    }
    assert {field["key"] for field in healthcare["configuration_fields"]} >= {
        "patients",
        "doctors",
        "appointments",
        "hospitals",
        "medical_claims",
    }
    assert not healthcare["generation_available"]
