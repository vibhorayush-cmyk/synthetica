"""Application service for generation history."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.history.models import HistoryEntry
from app.history.repository import HistoryRepository, build_history_id
from app.models.generation import GenerateResponse
from app.services.generation_service import GenerationService, get_generation_service


class HistoryService:
    """Store and serve generation history metadata."""

    def __init__(
        self,
        repository: HistoryRepository,
        generation_service: GenerationService | None = None,
    ) -> None:
        self._repository = repository
        self._generation_service = generation_service or get_generation_service()

    def list_history(self) -> list[HistoryEntry]:
        return self._repository.list()

    def get_history_entry(self, entry_id: str) -> HistoryEntry:
        return self._repository.get(entry_id)

    def delete_history_entry(self, entry_id: str) -> None:
        self._repository.delete(entry_id)

    def delete_all_history(self) -> None:
        self._repository.delete_all()

    def record_generation(
        self,
        response: GenerateResponse,
        request: object,
        template_name: str | None = None,
    ) -> HistoryEntry:
        zip_path = Path(response.download_url)
        entry = HistoryEntry(
            id=build_history_id(),
            dataset_name=f"Dataset {datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            industry="retail",
            scenario=response.scenario,
            template_name=template_name,
            quality=response.quality,
            customers=0,
            products=0,
            stores=0,
            orders=0,
            export_type="zip",
            zip_filename=zip_path.name,
            zip_size=0,
            generated_at=response.generated_at,
            generation_duration_ms=0,
            status="completed",
            challenge_title=response.challenge_title,
            generated_files=response.generated_files,
            readme_preview="Generated dataset bundle ready for review.",
            data_dictionary_preview="Data dictionary available in the export bundle.",
        )
        return self._repository.create(entry)

    def regenerate(self, entry_id: str) -> GenerateResponse:
        return GenerateResponse(
            download_url="",
            generated_files=[],
            row_counts={},
            generated_at=datetime.now(timezone.utc),
            scenario="none",
            quality={},
            challenge_title="",
            difficulty="",
            estimated_time="",
            challenge_pdf_url="",
        )

    def clone(self, entry_id: str) -> HistoryEntry:
        entry = self.get_history_entry(entry_id)
        cloned = entry.model_copy(
            update={
                "id": build_history_id(),
                "dataset_name": f"{entry.dataset_name} Copy",
                "generated_at": datetime.now(timezone.utc),
            }
        )
        return self._repository.create(cloned)
