from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_v1_health_and_readiness_endpoints() -> None:
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    readiness = client.get("/api/v1/readyz")
    assert readiness.status_code == 200
    assert readiness.json()["status"] == "ready"


def test_metrics_endpoint_reports_runtime_stats() -> None:
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "synthetic-analytics-data-generator"
    assert payload["requests"] >= 0
    assert payload["plugins"] >= 1
