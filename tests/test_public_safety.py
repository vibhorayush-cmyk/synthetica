"""Regression tests for public-facing generation safeguards."""

import logging
import os
from pathlib import Path
from time import sleep, time
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.routes import generation
from app.core.logging import JsonFormatter
from app.core.middleware import RateLimitMiddleware
from app.core.settings import Settings
from app.exporters.storage import ExportStorageLimitError, ExportStorageManager
from app.main import app
from app.models.generation import GenerateRequest
from app.services.generation_service import get_generation_service
from conftest import auth_headers


def test_retail_limit_returns_a_clear_environment_message(monkeypatch) -> None:
    """Field limits explain the configured boundary a deployer can change."""
    configured = Settings(max_customers=2, max_total_rows=100)
    monkeypatch.setattr("app.models.generation.get_settings", lambda: configured)

    with pytest.raises(ValidationError, match=r"MAX_CUSTOMERS \(2\)"):
        GenerateRequest(
            industry="retail", customers=3, products=1, stores=1, orders=1
        )


def test_total_rows_limit_accounts_for_retail_order_items(monkeypatch) -> None:
    """Retail estimates include both order and order-item rows before execution."""
    configured = Settings(max_total_rows=5)
    monkeypatch.setattr("app.models.generation.get_settings", lambda: configured)

    with pytest.raises(ValidationError, match=r"MAX_TOTAL_ROWS \(5\)"):
        GenerateRequest(
            industry="retail", customers=1, products=1, stores=1, orders=2
        )


def test_generation_endpoint_has_a_separate_rate_limit() -> None:
    """Expensive generation calls are throttled independently of normal writes."""
    limited_app = FastAPI()
    limited_app.add_middleware(
        RateLimitMiddleware,
        settings=Settings(
            rate_limit_requests=10,
            generation_rate_limit_requests=1,
            generation_rate_limit_window_seconds=60,
        ),
    )

    @limited_app.post("/generate")
    async def generate() -> dict[str, bool]:
        return {"ok": True}

    with TestClient(limited_app) as client:
        assert client.post("/generate").status_code == 200
        response = client.post("/generate")

    assert response.status_code == 429
    assert response.json()["detail"].startswith("Too many generation requests")
    assert response.headers["retry-after"] == "60"


def test_generation_timeout_returns_actionable_error(monkeypatch, api_client) -> None:
    """A slow service produces a bounded 504 response instead of hanging clients."""

    class SlowService:
        def generate(self, _: GenerateRequest) -> None:
            sleep(0.05)

    app.dependency_overrides[get_generation_service] = SlowService
    monkeypatch.setattr(
        generation,
        "settings",
        SimpleNamespace(generation_timeout_seconds=0.001),
    )
    try:
        client = api_client
        response = client.post(
                "/generate",
                headers=auth_headers(client),
                json={
                    "industry": "retail",
                    "customers": 1,
                    "products": 1,
                    "stores": 1,
                    "orders": 1,
                },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 504
    assert "Reduce the dataset size" in response.json()["detail"]


def test_export_storage_expires_old_entries_and_enforces_capacity(tmp_path: Path) -> None:
    """Expired exports are removed first and capacity removes oldest remaining bundles."""
    expired = tmp_path / "expired.zip"
    expired.write_bytes(b"old")
    os.utime(expired, (time() - 7_200, time() - 7_200))

    manager = ExportStorageManager(tmp_path, ttl_hours=1, max_storage_mb=1)
    result = manager.maintain()

    assert result.expired_entries_removed == 1
    assert not expired.exists()

    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    first.write_bytes(b"a" * 700_000)
    second.write_bytes(b"b" * 700_000)
    os.utime(first, (time() - 10, time() - 10))
    bounded = manager.maintain()

    assert bounded.capacity_entries_removed == 1
    assert not first.exists()
    assert second.exists()
    assert bounded.usage_bytes <= 1024 * 1024


def test_export_storage_rejects_an_export_that_cannot_fit(tmp_path: Path) -> None:
    """A protected active bundle is never deleted merely to satisfy the cap."""
    active = tmp_path / "active.zip"
    active.write_bytes(b"x" * (1024 * 1024 + 1))
    manager = ExportStorageManager(tmp_path, ttl_hours=1, max_storage_mb=1)

    with pytest.raises(ExportStorageLimitError, match="Export storage is full"):
        manager.maintain({active})

    assert active.exists()


def test_generation_logs_keep_safe_structured_context() -> None:
    """Generation logs are machine-readable and omit data rows and file paths."""
    record = logging.LogRecord(
        "app.services.generation_service",
        logging.INFO,
        __file__,
        1,
        "dataset_generated",
        (),
        None,
    )
    record.industry = "retail"  # type: ignore[attr-defined]
    record.rows = 42  # type: ignore[attr-defined]
    rendered = JsonFormatter().format(record)

    assert '"industry": "retail"' in rendered
    assert '"rows": 42' in rendered
    assert "customers.csv" not in rendered
