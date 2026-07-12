"""Integration tests for the dataset generation API."""

from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes import generation
from app.exporters import ExportService
from app.main import app
from app.services.generation_service import GenerationService, get_generation_service
from conftest import auth_headers


def test_generate_retail_dataset_and_download_zip(tmp_path: Path, monkeypatch, api_client) -> None:
    """Generating retail data returns metadata and a downloadable ZIP archive."""
    service = GenerationService(
        ExportService(
            exports_root=tmp_path,
            clock=lambda: datetime(2026, 7, 12, 14, 30, 45),
        )
    )
    app.dependency_overrides[get_generation_service] = lambda: service
    monkeypatch.setattr(generation, "EXPORTS_DIR", tmp_path)

    try:
        client = api_client
        headers = auth_headers(client)
        response = client.post(
                "/generate",
                headers=headers,
                json={
                    "industry": "retail",
                    "customers": 2,
                    "products": 2,
                    "stores": 1,
                    "orders": 10,
                    "export": "zip",
                    "quality": {"missing_values": 5},
                },
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["row_counts"] == {
                "customers": 2,
                "products": 2,
                "stores": 1,
                "orders": 10,
                "order_items": 10,
        }
        assert payload["generated_at"] == "2026-07-12T14:30:45"
        assert payload["scenario"] == "none"
        assert payload["quality"] == {
                "missing_values": 5.0,
                "duplicates": 0.0,
                "outliers": 0.0,
                "invalid_formats": 0.0,
                "referential_noise": 0.0,
        }
        assert set(payload["generated_files"]) == {
                "customers.csv",
                "products.csv",
                "stores.csv",
                "orders.csv",
                "order_items.csv",
                "data_dictionary.xlsx",
                "README.md",
                "challenge.md",
                "challenge.pdf",
                "requirements.md",
                "dataset_overview.md",
        }
        assert payload["challenge_title"] == "Retail Performance Investigation"
        assert payload["difficulty"] == "Intermediate"
        assert payload["estimated_time"] == "6–8 hours"

        download = client.get(payload["download_url"], headers=headers)
        assert download.status_code == 200
        assert download.headers["content-type"] == "application/zip"
        challenge_pdf = client.get(payload["challenge_pdf_url"], headers=headers)
        assert challenge_pdf.status_code == 200
        assert challenge_pdf.headers["content-type"] == "application/pdf"
        history = client.get("/history", headers=headers)
        assert history.status_code == 200
        assert len(history.json()) == 1
        assert history.json()[0]["zip_filename"] == Path(payload["download_url"]).name
    finally:
        app.dependency_overrides.clear()


def test_generate_rejects_unsupported_industry(api_client) -> None:
    """Only explicitly supported industries pass API request validation."""
    client = api_client
    response = client.post(
            "/generate",
            headers=auth_headers(client),
            json={
                "industry": "healthcare",
                "customers": 2,
                "products": 2,
                "stores": 1,
                "orders": 10,
                "export": "zip",
            },
    )

    assert response.status_code == 422


def test_download_returns_not_found_for_missing_archive(api_client) -> None:
    """The download route does not expose arbitrary or missing files."""
    client = api_client
    response = client.get("/downloads/missing.zip", headers=auth_headers(client))

    assert response.status_code == 404
