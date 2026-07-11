"""Pydantic schemas for history API payloads."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.history.models import HistoryEntry


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
