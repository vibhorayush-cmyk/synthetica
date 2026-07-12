"""Pydantic schemas for history API payloads."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.history.models import HistoryEntry
from app.db.models import GenerationHistory


class HistoryEntryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    dataset_name: str
    industry: str
    scenario: str
    template_name: str | None = None
    quality: dict[str, float]
    customers: int
    products: int
    stores: int
    orders: int
    export_type: str
    zip_filename: str
    zip_size: int
    generated_at: datetime
    generation_duration_ms: int
    status: str
    challenge_title: str | None = None
    generated_files: list[str] = Field(default_factory=list)
    readme_preview: str | None = None
    data_dictionary_preview: str | None = None

    @classmethod
    def from_model(cls, model: "HistoryEntry") -> "HistoryEntryResponse":
        return cls(**model.to_payload())

    @classmethod
    def from_record(cls, record: GenerationHistory) -> "HistoryEntryResponse":
        """Adapt the database record without changing the existing response contract."""
        configuration = record.configuration
        return cls(
            id=str(record.id),
            dataset_name=record.dataset_name,
            industry=record.industry,
            scenario=record.scenario,
            quality=record.quality,
            customers=configuration.get("customers", 0),
            products=configuration.get("products", 0),
            stores=configuration.get("stores", 0),
            orders=configuration.get("orders", 0),
            export_type=record.export_type,
            zip_filename=record.download_filename,
            zip_size=record.dataset_size,
            generated_at=record.generated_at,
            generation_duration_ms=record.generation_duration_ms,
            status=record.status,
            challenge_title=record.challenge_title,
            generated_files=record.generated_files,
            readme_preview="Generated dataset bundle ready for review.",
            data_dictionary_preview="Data dictionary available in the export bundle.",
        )
