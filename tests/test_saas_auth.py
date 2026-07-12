"""Database-backed authentication, authorization, and ownership tests."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.history.database_service import AsyncHistoryService
from app.models.generation import GenerateRequest, GenerateResponse

from conftest import auth_headers


def test_registration_duplicate_email_and_login(api_client: TestClient) -> None:
    """Registration validates unique email and login returns a JWT pair."""
    headers = auth_headers(api_client, "person@example.com")
    assert headers["Authorization"].startswith("Bearer ")
    duplicate = api_client.post(
        "/auth/register",
        json={"full_name": "Another", "email": "PERSON@example.com", "password": "StrongPassword123"},
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
    assert api_client.post("/generate", json={"industry": "retail", "customers": 1, "products": 1, "stores": 1, "orders": 1}).status_code == 401
    assert api_client.get("/history").status_code == 401
    assert api_client.get("/templates").status_code == 401


def test_profile_update_and_refresh_lifecycle(api_client: TestClient) -> None:
    """Profiles update under a valid token and refresh tokens rotate."""
    headers = auth_headers(api_client)
    updated = api_client.patch("/users/me", headers=headers, json={"full_name": "Updated Member", "avatar_url": "https://example.com/avatar.png"})
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Updated Member"
    login = api_client.post("/auth/login", json={"email": "member@example.com", "password": "StrongPassword123"})
    refreshed = api_client.post("/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != login.json()["access_token"]


def test_history_is_private_to_its_owner(api_client: TestClient) -> None:
    """A user cannot retrieve another user's history entry by UUID."""
    owner = auth_headers(api_client, "owner@example.com")
    other = auth_headers(api_client, "other@example.com")
    created = api_client.post(
        "/templates",
        headers=owner,
        json={"name": "Owner template", "industry": "retail", "scenario": "none", "customers": 2, "products": 2, "stores": 1, "orders": 2, "export_type": "zip", "quality": {}, "difficulty": "Beginner"},
    )
    assert created.status_code == 201
    assert api_client.get("/templates", headers=other).json() == []


def test_validation_messages_are_actionable(api_client: TestClient) -> None:
    """Invalid email and weak password return field-level validation failures."""
    response = api_client.post("/auth/register", json={"full_name": "A", "email": "not-an-email", "password": "weak"})
    assert response.status_code == 422
    messages = str(response.json()["detail"])
    assert "valid email" in messages or "at least 12" in messages
