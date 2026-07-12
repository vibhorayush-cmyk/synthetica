"""Direct application-service tests for async SaaS persistence boundaries."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth.schemas import (
    LoginRequest,
    PasswordResetConfirm,
    ProfileUpdateRequest,
    RegistrationRequest,
)
from app.auth.service import AuthenticationError, AuthService
from app.core.settings import Settings
from app.db.base import Base
from app.history.database_service import AsyncHistoryService
from app.models.generation import GenerateRequest, GenerateResponse
from app.templates.database_service import AsyncTemplateService
from app.templates.schemas import TemplateCreate, TemplateUpdate


def test_async_saas_services_cover_security_and_user_owned_records(tmp_path) -> None:
    """Exercise service error paths without depending on HTTP middleware behavior."""

    async def exercise() -> None:
        engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'services.db'}")
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        settings = Settings(
            database_url=f"sqlite+aiosqlite:///{tmp_path / 'services.db'}",
            export_dir=tmp_path,
            secret_key="service-test-secret-key-with-32-characters",
        )
        try:
            async with factory() as session:
                auth = AuthService(session, settings)
                registration = RegistrationRequest(
                    full_name="Service Member",
                    email="service@example.com",
                    password="StrongPassword123",
                )
                user, initial_tokens = await auth.register(registration)

                with pytest.raises(ValueError, match="already exists"):
                    await auth.register(registration)
                with pytest.raises(AuthenticationError, match="invalid email"):
                    await auth.login(
                        LoginRequest(
                            email=user.email,
                            password="WrongPassword123",
                        )
                    )

                await auth.refresh(initial_tokens.refresh_token)
                with pytest.raises(AuthenticationError, match="invalid or expired"):
                    await auth.refresh(initial_tokens.refresh_token)
                other_user, other_tokens = await auth.register(
                    RegistrationRequest(
                        full_name="Other Service Member",
                        email="other-service@example.com",
                        password="StrongPassword123",
                    )
                )
                with pytest.raises(AuthenticationError, match="does not belong"):
                    await auth.logout(user, other_tokens.refresh_token)
                await auth.logout(other_user, other_tokens.refresh_token)

                with pytest.raises(AuthenticationError, match="current password"):
                    await auth.update_profile(
                        user,
                        ProfileUpdateRequest(
                            password="ChangedPassword456",
                            current_password="WrongPassword123",
                        ),
                    )
                updated = await auth.update_profile(
                    user,
                    ProfileUpdateRequest(
                        full_name="Updated Service Member",
                        avatar_url="https://example.com/avatar.png",
                        password="ChangedPassword456",
                        current_password="StrongPassword123",
                    ),
                )
                assert updated.full_name == "Updated Service Member"
                assert updated.avatar_url == "https://example.com/avatar.png"
                assert auth.verify_password("ChangedPassword456", updated.password_hash)
                assert not auth.verify_password("password", "not-a-bcrypt-hash")

                assert (
                    await auth.create_password_reset_token("missing@example.com") == ""
                )
                reset_token = await auth.create_password_reset_token(updated.email)
                await auth.reset_password(
                    PasswordResetConfirm(
                        token=reset_token,
                        password="ResetPassword789",
                    )
                )
                assert (
                    await auth.login(
                        LoginRequest(
                            email=updated.email,
                            password="ResetPassword789",
                        )
                    )
                ).access_token

                templates = AsyncTemplateService(session)
                template = await templates.create(
                    updated.id,
                    TemplateCreate(
                        name="Service template",
                        industry="retail",
                        scenario="none",
                        customers=2,
                        products=2,
                        stores=1,
                        orders=2,
                    ),
                )
                template_id = UUID(template.id)
                assert len(await templates.list(updated.id)) == 1
                assert (
                    await templates.get(template_id, updated.id)
                ).name == template.name
                request = await templates.generate_request(template_id, updated.id)
                assert request.normalized_configuration()["orders"] == 2
                revised = await templates.update(
                    template_id,
                    updated.id,
                    TemplateUpdate(name="Revised template", orders=3),
                )
                assert revised.version == 2
                with pytest.raises(ValueError, match="template not found"):
                    await templates.get(template_id, uuid4())

                history = AsyncHistoryService(session, settings)
                response = GenerateResponse(
                    download_url="/downloads/service.zip",
                    generated_files=["customers.csv"],
                    row_counts={"customers": 2},
                    generated_at=datetime(2026, 7, 13, tzinfo=UTC),
                    scenario="none",
                    quality={},
                    challenge_title="Service challenge",
                    difficulty="Beginner",
                    estimated_time="1 hour",
                    challenge_pdf_url="/downloads/service/challenge.pdf",
                )
                entry = await history.record_generation(
                    updated.id,
                    GenerateRequest(
                        industry="retail",
                        customers=2,
                        products=2,
                        stores=1,
                        orders=2,
                    ),
                    response,
                    duration_ms=25,
                )
                assert (await history.get(entry.id, updated.id)).status == "completed"
                clone = await history.clone(entry.id, updated.id)
                assert clone.status == "cloned"
                await history.delete(entry.id, updated.id)
                with pytest.raises(ValueError, match="history entry not found"):
                    await history.get(entry.id, updated.id)
                await history.delete_all(updated.id)
                assert await history.list(updated.id) == []
                await templates.delete(template_id, updated.id)
        finally:
            await engine.dispose()

    asyncio.run(exercise())
