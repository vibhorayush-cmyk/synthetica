"""Shared isolated async-database fixtures for SaaS API tests."""

import asyncio
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app


@pytest.fixture
def api_client(tmp_path) -> Iterator[TestClient]:
    """Run API tests against a fresh async SQLite schema, never PostgreSQL."""
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'saas.db'}")
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def create_schema() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def override_session():
        async with factory() as session:
            yield session

    asyncio.run(create_schema())
    app.dependency_overrides[get_db_session] = override_session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        asyncio.run(engine.dispose())


def auth_headers(client: TestClient, email: str = "member@example.com") -> dict[str, str]:
    """Register one valid user and return its bearer authorization header."""
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Synthetica Member",
            "email": email,
            "password": "StrongPassword123",
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
