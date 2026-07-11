"""Domain models for dataset templates."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TemplateModel(BaseModel):
    """Persisted dataset template configuration."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    industry: str = Field(min_length=1, max_length=100)
    scenario: str = Field(default="none", min_length=1, max_length=100)
    customers: int = Field(ge=1, le=1_000_000)
    products: int = Field(ge=1, le=1_000_000)
    stores: int = Field(ge=1, le=100_000)
    orders: int = Field(ge=1, le=1_000_000)
    export_type: str = Field(default="zip", min_length=1, max_length=50)
    quality: dict[str, float] = Field(default_factory=dict)
    difficulty: str = Field(default="Beginner", min_length=1, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1, ge=1)

    def to_payload(self) -> dict[str, Any]:
        """Return a serializable payload."""
        return self.model_dump(mode="json")
