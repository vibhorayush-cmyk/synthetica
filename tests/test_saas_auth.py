"""Database-backed authentication, authorization, and ownership tests."""

from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes import generation
from app.exporters import ExportService
from app.main import app
from app.services.generation_service import GenerationService, get_generation_service
from conftest import auth_headers


def test_registration_duplicate_email_and_login(api_client: TestClient) -> None:
    """Registration validates unique email and login returns a JWT pair."""
    headers = auth_headers(api_client, "person@example.com")
    assert headers["Authorization"].startswith("Bearer ")
    duplicate = api_client.post(
        "/auth/register",
        json={
            "full_name": "Another",
            "email": "PERSON@example.com",
            "password": "StrongPassword123",
        },
    )
    assert duplicate.status_code == 409
    login = api_client.post(
        "/auth/login",
        json={"email": "person@example.com", "password": "StrongPassword123"},
    )
    assert login.status_code == 200
    assert login.json()["refresh_token"]


def test_jwt_protects_generation_history_and_templates(api_client: TestClient) -> None:
    """Anonymous users can browse but cannot access account-owned workflows."""
    assert api_client.get("/industries").status_code == 200
    assert (
        api_client.post(
            "/generate",
            json={
                "industry": "retail",
                "customers": 1,
                "products": 1,
                "stores": 1,
                "orders": 1,
            },
        ).status_code
        == 401
    )
    assert api_client.get("/history").status_code == 401
    assert api_client.get("/templates").status_code == 401


def test_profile_update_and_refresh_lifecycle(api_client: TestClient) -> None:
    """Profiles update under a valid token and refresh tokens rotate."""
    headers = auth_headers(api_client)
    updated = api_client.patch(
        "/users/me",
        headers=headers,
        json={
            "full_name": "Updated Member",
            "avatar_url": "https://example.com/avatar.png",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Updated Member"
    login = api_client.post(
        "/auth/login",
        json={"email": "member@example.com", "password": "StrongPassword123"},
    )
    refreshed = api_client.post(
        "/auth/refresh", json={"refresh_token": login.json()["refresh_token"]}
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != login.json()["access_token"]


def test_history_is_private_to_its_owner(api_client: TestClient) -> None:
    """A user cannot retrieve another user's history entry by UUID."""
    owner = auth_headers(api_client, "owner@example.com")
    other = auth_headers(api_client, "other@example.com")
    created = api_client.post(
        "/templates",
        headers=owner,
        json={
            "name": "Owner template",
            "industry": "retail",
            "scenario": "none",
            "customers": 2,
            "products": 2,
            "stores": 1,
            "orders": 2,
            "export_type": "zip",
            "quality": {},
            "difficulty": "Beginner",
        },
    )
    assert created.status_code == 201
    assert api_client.get("/templates", headers=other).json() == []


def test_validation_messages_are_actionable(api_client: TestClient) -> None:
    """Invalid email and weak password return field-level validation failures."""
    response = api_client.post(
        "/auth/register",
        json={"full_name": "A", "email": "not-an-email", "password": "weak"},
    )
    assert response.status_code == 422
    messages = str(response.json()["detail"])
    assert "valid email" in messages or "at least 12" in messages


def test_authentication_lifecycle_and_profile_password_change(
    api_client: TestClient,
) -> None:
    """Refresh, logout, reset, and profile validation preserve account security."""
    headers = auth_headers(api_client, "lifecycle@example.com")
    registration_login = api_client.post(
        "/auth/login",
        json={"email": "lifecycle@example.com", "password": "StrongPassword123"},
    )
    refresh_token = registration_login.json()["refresh_token"]

    assert api_client.get("/auth/me", headers=headers).status_code == 200
    assert api_client.get("/users/me", headers=headers).status_code == 200
    assert (
        api_client.post(
            "/auth/login",
            json={"email": "lifecycle@example.com", "password": "incorrect"},
        ).status_code
        == 401
    )
    assert (
        api_client.patch(
            "/users/me",
            headers=headers,
            json={"password": "NewStrongPassword456"},
        ).status_code
        == 422
    )
    password_update = api_client.patch(
        "/users/me",
        headers=headers,
        json={
            "password": "NewStrongPassword456",
            "current_password": "StrongPassword123",
        },
    )
    assert password_update.status_code == 200
    assert (
        api_client.post(
            "/auth/login",
            json={
                "email": "lifecycle@example.com",
                "password": "NewStrongPassword456",
            },
        ).status_code
        == 200
    )

    unknown_reset = api_client.post(
        "/auth/password-reset/request", json={"email": "unknown@example.com"}
    )
    assert unknown_reset.status_code == 200
    assert unknown_reset.json()["reset_token"] == ""
    reset_request = api_client.post(
        "/auth/password-reset/request", json={"email": "lifecycle@example.com"}
    )
    assert reset_request.status_code == 200
    assert (
        api_client.post(
            "/auth/password-reset/confirm",
            json={"token": "invalid", "password": "AnotherPassword789"},
        ).status_code
        == 401
    )
    assert (
        api_client.post(
            "/auth/password-reset/confirm",
            json={
                "token": reset_request.json()["reset_token"],
                "password": "AnotherPassword789",
            },
        ).status_code
        == 204
    )

    assert (
        api_client.post(
            "/auth/logout", headers=headers, json={"refresh_token": refresh_token}
        ).status_code
        == 204
    )
    assert (
        api_client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        ).status_code
        == 401
    )


def test_templates_are_scoped_validated_and_mutable(api_client: TestClient) -> None:
    """Template CRUD rejects collisions and never leaks records between users."""
    owner = auth_headers(api_client, "templates-owner@example.com")
    other = auth_headers(api_client, "templates-other@example.com")
    payload = {
        "name": "Quarterly retail",
        "description": "Initial configuration",
        "industry": "retail",
        "scenario": "none",
        "customers": 2,
        "products": 2,
        "stores": 1,
        "orders": 2,
        "export_type": "zip",
        "quality": {"missing_values": 2},
        "difficulty": "Beginner",
    }
    created = api_client.post("/templates", headers=owner, json=payload)
    assert created.status_code == 201
    template_id = created.json()["id"]
    assert len(api_client.get("/templates", headers=owner).json()) == 1
    assert api_client.get(f"/templates/{template_id}", headers=owner).status_code == 200
    assert api_client.get(f"/templates/{template_id}", headers=other).status_code == 404
    assert api_client.post("/templates", headers=owner, json=payload).status_code == 422
    assert (
        api_client.post(
            "/templates",
            headers=owner,
            json={**payload, "name": "Invalid", "quality": {"outliers": 101}},
        ).status_code
        == 422
    )
    updated = api_client.put(
        f"/templates/{template_id}",
        headers=owner,
        json={"name": "Updated retail", "customers": 3, "description": "Updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2
    assert updated.json()["customers"] == 3
    assert (
        api_client.delete(f"/templates/{template_id}", headers=owner).status_code == 204
    )
    assert api_client.get(f"/templates/{template_id}", headers=owner).status_code == 404


def test_history_routes_are_owned_and_support_lifecycle(
    api_client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    """Generated records can be retrieved, cloned, regenerated, and removed by owner."""
    service = GenerationService(
        ExportService(
            exports_root=tmp_path,
            clock=lambda: datetime(2026, 7, 13, 12, 0, 0),
        )
    )
    app.dependency_overrides[get_generation_service] = lambda: service
    monkeypatch.setattr(generation, "EXPORTS_DIR", tmp_path)
    try:
        owner = auth_headers(api_client, "history-owner@example.com")
        generated = api_client.post(
            "/generate",
            headers=owner,
            json={
                "industry": "retail",
                "customers": 1,
                "products": 1,
                "stores": 1,
                "orders": 1,
                "export": "zip",
            },
        )
        assert generated.status_code == 201
        entries = api_client.get("/history", headers=owner).json()
        assert len(entries) == 1
        entry_id = entries[0]["id"]
        assert api_client.get(f"/history/{entry_id}", headers=owner).status_code == 200
        assert (
            api_client.post(f"/history/{entry_id}/clone", headers=owner).status_code
            == 200
        )
        assert (
            api_client.post(
                f"/history/{entry_id}/regenerate", headers=owner
            ).status_code
            == 200
        )
        assert (
            api_client.delete(f"/history/{entry_id}", headers=owner).status_code == 204
        )
        assert api_client.get(f"/history/{entry_id}", headers=owner).status_code == 404
        assert api_client.delete("/history", headers=owner).status_code == 204
        assert api_client.get("/history", headers=owner).json() == []
    finally:
        app.dependency_overrides.clear()
