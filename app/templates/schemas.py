"""Pydantic schemas for template API payloads."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.templates.models import TemplateModel


class TemplateCreate(BaseModel):
    """Payload used to create a template."""

    model_config = ConfigDict(extra="forbid")

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


class TemplateUpdate(BaseModel):
    """Payload used to update a template."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    industry: str | None = Field(default=None, min_length=1, max_length=100)
    scenario: str | None = Field(default=None, min_length=1, max_length=100)
    customers: int | None = Field(default=None, ge=1, le=1_000_000)
    products: int | None = Field(default=None, ge=1, le=1_000_000)
    stores: int | None = Field(default=None, ge=1, le=100_000)
    orders: int | None = Field(default=None, ge=1, le=1_000_000)
    export_type: str | None = Field(default=None, min_length=1, max_length=50)
    quality: dict[str, float] | None = Field(default=None)
    difficulty: str | None = Field(default=None, min_length=1, max_length=100)


class TemplateResponse(BaseModel):
    """Template payload returned by the API."""

    id: str
    name: str
    description: str
    industry: str
    scenario: str
    customers: int
    products: int
    stores: int
    orders: int
    export_type: str
    quality: dict[str, float]
    difficulty: str
    created_at: datetime
    updated_at: datetime
    version: int

    @classmethod
    def from_model(cls, model: TemplateModel) -> "TemplateResponse":
        return cls(**model.to_payload())
