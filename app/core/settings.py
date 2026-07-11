"""Environment-backed application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Validated deployment configuration loaded from ``.env``."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Synthetic Analytics Platform"
    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///./data/app.db"
    export_dir: Path = BASE_DIR / "exports"
    history_dir: Path = BASE_DIR / "history"
    template_dir: Path = BASE_DIR / "templates"
    secret_key: SecretStr = SecretStr("change-me-in-production")
    cors_origins: list[AnyHttpUrl] = Field(
        default_factory=lambda: [AnyHttpUrl("http://localhost:3000")]
    )
    max_dataset_rows: int = Field(default=1_000_000, ge=1, le=10_000_000)
    rate_limit_requests: int = Field(default=30, ge=1, le=10_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug(cls, value: object) -> object:
        """Accept conventional deployment labels from inherited environments."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"development", "dev"}:
                return True
        return value

    @property
    def cors_origin_strings(self) -> list[str]:
        """Return CORS origins in the format FastAPI expects."""
        return [str(origin).rstrip("/") for origin in self.cors_origins]


@lru_cache
def get_settings() -> Settings:
    """Create settings once per process."""
    return Settings()
