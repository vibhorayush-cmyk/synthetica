"""Tests for deployment-facing API infrastructure."""

from fastapi.testclient import TestClient

from app.core.metrics import GenerationMetrics
from app.core.settings import Settings
from app.main import app


def test_versioned_health_endpoints_emit_request_ids() -> None:
    """Liveness and readiness are available through the versioned API."""
    with TestClient(app) as client:
        health = client.get("/api/v1/health", headers={"X-Request-ID": "test-id"})
        ready = client.get("/api/v1/ready")

    assert health.status_code == 200
    assert health.headers["X-Request-ID"] == "test-id"
    assert ready.json() == {"status": "ready"}


def test_root_service_metadata_is_available() -> None:
    """The legacy root remains a lightweight service discovery endpoint."""
    with TestClient(app) as client:
        response = client.get("/")

    assert response.json()["status"] == "ready"


def test_metrics_aggregate_generation_statistics() -> None:
    """Metrics preserve success, failure, duration, and memory aggregates."""
    local_metrics = GenerationMetrics()
    local_metrics.record_success(20, 5, 1_024)
    local_metrics.record_failure()

    assert local_metrics.snapshot() == {
        "generation_count": 1,
        "generation_failures": 1,
        "average_generation_duration_ms": 20.0,
        "total_export_duration_ms": 5.0,
        "peak_memory_bytes": 1_024,
    }


def test_settings_normalize_release_debug_value() -> None:
    """Common inherited deployment labels cannot prevent configuration loading."""
    settings = Settings(debug="release", cors_origins=["http://localhost:3000"])

    assert settings.debug is False
    assert settings.cors_origin_strings == ["http://localhost:3000"]

    development = Settings(debug="development", cors_origins=["http://localhost:3000"])
    assert development.debug is True
