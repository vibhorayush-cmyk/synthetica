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
    database_url: str = "postgresql+asyncpg://synthetica:synthetica@localhost:5432/synthetica"
    export_dir: Path = BASE_DIR / "exports"
    history_dir: Path = BASE_DIR / "history"
    template_dir: Path = BASE_DIR / "templates"
    secret_key: SecretStr = SecretStr(
        "development-only-secret-change-before-production-please"
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1_440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=90)
    password_reset_expire_minutes: int = Field(default=30, ge=5, le=1_440)
    cors_origins: list[AnyHttpUrl] = Field(
        default_factory=lambda: [AnyHttpUrl("http://localhost:3000")]
    )
    max_dataset_rows: int = Field(default=1_000_000, ge=1, le=10_000_000)
    # Retail uses the public, backwards-compatible environment variable names
    # documented for deployments. Other plugins can define their own field set.
    max_customers: int = Field(default=25_000, ge=1)
    max_products: int = Field(default=2_000, ge=1)
    max_stores: int = Field(default=250, ge=1)
    max_orders: int = Field(default=100_000, ge=1)
    max_banking_customers: int = Field(default=25_000, ge=1)
    max_banking_accounts: int = Field(default=50_000, ge=1)
    max_banking_transactions: int = Field(default=100_000, ge=1)
    max_banking_loans: int = Field(default=20_000, ge=1)
    max_banking_branches: int = Field(default=250, ge=1)
    max_banking_credit_cards: int = Field(default=50_000, ge=1)
    max_total_rows: int = Field(default=500_000, ge=1)
    generation_timeout_seconds: int = Field(default=90, ge=1, le=3_600)
    rate_limit_requests: int = Field(default=30, ge=1, le=10_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)
    generation_rate_limit_requests: int = Field(default=5, ge=1, le=10_000)
    generation_rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)
    export_ttl_hours: int = Field(default=2, ge=1, le=24 * 30)
    max_export_storage_mb: int = Field(default=500, ge=1)
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    @property
    def jwt_secret(self) -> str:
        """Use the existing deployment secret as the JWT signing key."""
        return self.secret_key.get_secret_value()

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

    def industry_generation_limits(self, industry: str) -> dict[str, tuple[int, str]]:
        """Return environment-backed limits for a supported industry plugin."""
        limits = {
            "retail": {
                "customers": (self.max_customers, "MAX_CUSTOMERS"),
                "products": (self.max_products, "MAX_PRODUCTS"),
                "stores": (self.max_stores, "MAX_STORES"),
                "orders": (self.max_orders, "MAX_ORDERS"),
            },
            "banking": {
                "customers": (self.max_banking_customers, "MAX_BANKING_CUSTOMERS"),
                "accounts": (self.max_banking_accounts, "MAX_BANKING_ACCOUNTS"),
                "transactions": (
                    self.max_banking_transactions,
                    "MAX_BANKING_TRANSACTIONS",
                ),
                "loans": (self.max_banking_loans, "MAX_BANKING_LOANS"),
                "branches": (self.max_banking_branches, "MAX_BANKING_BRANCHES"),
                "credit_cards": (
                    self.max_banking_credit_cards,
                    "MAX_BANKING_CREDIT_CARDS",
                ),
            },
        }
        return limits.get(industry, {})


@lru_cache
def get_settings() -> Settings:
    """Create settings once per process."""
    return Settings()
