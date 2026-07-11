"""Domain models for generation history entries."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HistoryEntry(BaseModel):
    """Persisted metadata for a generated dataset bundle."""

    model_config = ConfigDict(extra="forbid")

    id: str
    dataset_name: str = Field(min_length=1, max_length=200)
    industry: str = Field(min_length=1, max_length=100)
    scenario: str = Field(default="none", min_length=1, max_length=100)
    template_name: str | None = None
    quality: dict[str, float] = Field(default_factory=dict)
    customers: int = Field(ge=1, le=1_000_000)
    products: int = Field(ge=1, le=1_000_000)
    stores: int = Field(ge=1, le=100_000)
    orders: int = Field(ge=1, le=1_000_000)
    export_type: str = Field(default="zip", min_length=1, max_length=50)
    zip_filename: str = Field(min_length=1, max_length=300)
    zip_size: int = Field(ge=0)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generation_duration_ms: int = Field(ge=0)
    status: str = Field(default="completed", min_length=1, max_length=50)
    challenge_title: str | None = None
    generated_files: list[str] = Field(default_factory=list)
    readme_preview: str | None = None
    data_dictionary_preview: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
