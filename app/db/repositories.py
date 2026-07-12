"""Async repository implementations for SaaS-owned records."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GenerationHistory, RefreshToken, SavedDataset, Template, User


class UserRepository:
    """Persistence boundary for user identities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, user_id: UUID) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def save(self, user: User) -> User:
        await self._session.commit()
        await self._session.refresh(user)
        return user


class RefreshTokenRepository:
    """Persist refresh-token rotation and revocation state."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        self._session.add(token)
        await self._session.commit()
        await self._session.refresh(token)
        return token

    async def get_active(self, token_id: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.token_id == token_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken, revoked_at: datetime) -> None:
        token.revoked_at = revoked_at
        await self._session.commit()


class GenerationHistoryRepository:
    """User-scoped storage for generation metadata."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: UUID) -> list[GenerationHistory]:
        result = await self._session.execute(
            select(GenerationHistory)
            .where(GenerationHistory.user_id == user_id)
            .order_by(GenerationHistory.generated_at.desc())
        )
        return list(result.scalars())

    async def get_for_user(
        self, entry_id: UUID, user_id: UUID
    ) -> GenerationHistory | None:
        result = await self._session.execute(
            select(GenerationHistory).where(
                GenerationHistory.id == entry_id,
                GenerationHistory.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self, entry: GenerationHistory, saved: SavedDataset
    ) -> GenerationHistory:
        self._session.add_all([entry, saved])
        await self._session.commit()
        await self._session.refresh(entry)
        return entry

    async def delete(self, entry: GenerationHistory) -> None:
        await self._session.delete(entry)
        await self._session.commit()

    async def delete_all_for_user(self, user_id: UUID) -> None:
        entries = await self.list_for_user(user_id)
        for entry in entries:
            await self._session.delete(entry)
        await self._session.commit()

    async def saved_dataset_for_user(
        self, filename: str, user_id: UUID
    ) -> SavedDataset | None:
        """Find an export only when it belongs to the requesting user."""
        result = await self._session.execute(
            select(SavedDataset).where(
                SavedDataset.filename == filename,
                SavedDataset.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()


class TemplateRepository:
    """User-scoped storage for reusable generator templates."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: UUID) -> list[Template]:
        result = await self._session.execute(
            select(Template)
            .where(Template.user_id == user_id)
            .order_by(Template.updated_at.desc())
        )
        return list(result.scalars())

    async def get_for_user(self, template_id: UUID, user_id: UUID) -> Template | None:
        result = await self._session.execute(
            select(Template).where(
                Template.id == template_id, Template.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, user_id: UUID, name: str) -> Template | None:
        result = await self._session.execute(
            select(Template).where(
                Template.user_id == user_id, Template.name.ilike(name)
            )
        )
        return result.scalar_one_or_none()

    async def create(self, template: Template) -> Template:
        self._session.add(template)
        await self._session.commit()
        await self._session.refresh(template)
        return template

    async def save(self, template: Template) -> Template:
        await self._session.commit()
        await self._session.refresh(template)
        return template

    async def delete(self, template: Template) -> None:
        await self._session.delete(template)
        await self._session.commit()
