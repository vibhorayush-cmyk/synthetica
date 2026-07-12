"""Async user-scoped generation-history application service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings, get_settings
from app.db.models import GenerationHistory, SavedDataset
from app.db.repositories import GenerationHistoryRepository
from app.history.schemas import HistoryEntryResponse
from app.models.generation import GenerateRequest, GenerateResponse


class AsyncHistoryService:
    """Persist and retrieve only the authenticated user's generated datasets."""

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self._repository = GenerationHistoryRepository(session)
        self._settings = settings or get_settings()

    async def record_generation(
        self,
        user_id: UUID,
        request: GenerateRequest,
        response: GenerateResponse,
        duration_ms: int,
        template_name: str | None = None,
    ) -> GenerationHistory:
        """Create linked history and saved-dataset records for one completed export."""
        filename = Path(response.download_url).name
        export_path = self._settings.export_dir / filename
        size = export_path.stat().st_size if export_path.is_file() else 0
        configuration = request.normalized_configuration()
        generated_at = response.generated_at
        entry = GenerationHistory(
            user_id=user_id,
            dataset_name=(
                f"{request.industry.title()} dataset "
                f"{generated_at.strftime('%Y-%m-%d %H:%M')}"
            ),
            industry=request.industry,
            scenario=response.scenario,
            configuration=configuration,
            quality=response.quality,
            export_type=request.export.value,
            download_filename=filename,
            dataset_size=size,
            status="completed",
            generation_duration_ms=max(duration_ms, 0),
            generated_at=generated_at,
            challenge_title=response.challenge_title,
            generated_files=response.generated_files,
        )
        saved = SavedDataset(
            user_id=user_id,
            history=entry,
            filename=filename,
            size_bytes=size,
            expires_at=datetime.now(UTC)
            + timedelta(hours=self._settings.export_ttl_hours),
        )
        return await self._repository.create(entry, saved)

    async def list(self, user_id: UUID) -> list[HistoryEntryResponse]:
        return [
            self._to_response(entry)
            for entry in await self._repository.list_for_user(user_id)
        ]

    async def get(self, entry_id: UUID, user_id: UUID) -> HistoryEntryResponse:
        entry = await self._repository.get_for_user(entry_id, user_id)
        if not entry:
            raise ValueError("history entry not found")
        return self._to_response(entry)

    async def delete(self, entry_id: UUID, user_id: UUID) -> None:
        entry = await self._repository.get_for_user(entry_id, user_id)
        if not entry:
            raise ValueError("history entry not found")
        await self._repository.delete(entry)

    async def delete_all(self, user_id: UUID) -> None:
        await self._repository.delete_all_for_user(user_id)

    async def clone(self, entry_id: UUID, user_id: UUID) -> HistoryEntryResponse:
        entry = await self._repository.get_for_user(entry_id, user_id)
        if not entry:
            raise ValueError("history entry not found")
        clone = GenerationHistory(
            user_id=user_id,
            dataset_name=f"{entry.dataset_name} Copy",
            industry=entry.industry,
            scenario=entry.scenario,
            configuration=entry.configuration,
            quality=entry.quality,
            export_type=entry.export_type,
            download_filename=entry.download_filename,
            dataset_size=entry.dataset_size,
            status="cloned",
            generation_duration_ms=0,
            generated_at=datetime.now(UTC),
            challenge_title=entry.challenge_title,
            generated_files=entry.generated_files,
        )
        saved = SavedDataset(
            user_id=user_id,
            history=clone,
            filename=clone.download_filename,
            size_bytes=clone.dataset_size,
            expires_at=entry.saved_dataset.expires_at if entry.saved_dataset else None,
        )
        return self._to_response(await self._repository.create(clone, saved))

    @staticmethod
    def _to_response(entry: GenerationHistory) -> HistoryEntryResponse:
        return HistoryEntryResponse.from_record(entry)
