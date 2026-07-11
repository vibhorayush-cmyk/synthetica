"""Models for generation requests and responses."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.settings import get_settings


class ExportFormat(StrEnum):
    """Supported downloadable export formats."""

    ZIP = "zip"


class QualityConfig(BaseModel):
    """Percentages of intentionally injected quality issues."""

    model_config = ConfigDict(extra="forbid")

    missing_values: float = Field(default=0, ge=0, le=100)
    duplicates: float = Field(default=0, ge=0, le=100)
    outliers: float = Field(default=0, ge=0, le=100)
    invalid_formats: float = Field(default=0, ge=0, le=100)
    referential_noise: float = Field(default=0, ge=0, le=100)

    def to_mapping(self) -> dict[str, float]:
        """Return a mapping accepted by the quality engine."""
        return self.model_dump()


class GenerateRequest(BaseModel):
    """Requested synthetic dataset parameters."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "industry": "retail",
                    "scenario": "black_friday",
                    "customers": 10_000,
                    "products": 500,
                    "stores": 50,
                    "orders": 100_000,
                    "export": "zip",
                    "quality": {"missing_values": 5, "duplicates": 2},
                }
            ]
        }
    )

    industry: str = Field(min_length=1, max_length=100)
    scenario: str = Field(default="none", min_length=1, max_length=100)
    customers: int | None = Field(default=None, ge=1, le=1_000_000)
    products: int | None = Field(default=None, ge=1, le=1_000_000)
    stores: int | None = Field(default=None, ge=1, le=100_000)
    orders: int | None = Field(default=None, ge=1, le=1_000_000)
    configuration: dict[str, int] = Field(default_factory=dict)
    export: ExportFormat = ExportFormat.ZIP
    quality: QualityConfig = Field(default_factory=QualityConfig)

    @model_validator(mode="after")
    def validate_deployment_row_limit(self) -> "GenerateRequest":
        """Enforce the deployment-configured dataset size boundary."""
        settings = get_settings()
        configuration = self.configuration or {
            key: value
            for key, value in {
                "customers": self.customers,
                "products": self.products,
                "stores": self.stores,
                "orders": self.orders,
            }.items()
            if value is not None
        }
        if not configuration:
            raise ValueError("configuration must include at least one positive field")
        if any(value < 1 for value in configuration.values()):
            raise ValueError("configuration values must be at least 1")
        if max(configuration.values()) > settings.max_dataset_rows:
            raise ValueError(
                f"configuration values must not exceed MAX_DATASET_ROWS ({settings.max_dataset_rows})"
            )
        return self


class GenerateResponse(BaseModel):
    """Location and identity of a generated export."""

    download_url: str
    generated_files: list[str]
    row_counts: dict[str, int]
    generated_at: datetime
    scenario: str
    quality: dict[str, float]
    challenge_title: str
    difficulty: str
    estimated_time: str
    challenge_pdf_url: str
