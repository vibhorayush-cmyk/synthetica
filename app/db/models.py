"""Database entities for users, datasets, history, and templates."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDTimestampMixin


class UserRole(StrEnum):
    """Authorization roles supported by the application."""

    ADMIN = "admin"
    USER = "user"


class User(UUIDTimestampMixin, Base):
    """Authenticated SaaS account."""

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.USER.value, nullable=False)

    history_entries: Mapped[list["GenerationHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    templates: Mapped[list["Template"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class GenerationHistory(UUIDTimestampMixin, Base):
    """One user-owned generation request and its exported artifact."""

    __tablename__ = "generation_history"
    __table_args__ = (
        Index("ix_generation_history_user_generated", "user_id", "generated_at"),
        Index("ix_generation_history_status", "status"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    scenario: Mapped[str] = mapped_column(String(100), nullable=False, default="none")
    configuration: Mapped[dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    quality: Mapped[dict[str, float]] = mapped_column(JSON, default=dict, nullable=False)
    export_type: Mapped[str] = mapped_column(String(50), default="zip", nullable=False)
    download_filename: Mapped[str] = mapped_column(String(300), nullable=False)
    dataset_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    generation_duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    challenge_title: Mapped[str | None] = mapped_column(String(300))
    generated_files: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    user: Mapped[User] = relationship(back_populates="history_entries")
    saved_dataset: Mapped["SavedDataset | None"] = relationship(
        back_populates="history", cascade="all, delete-orphan", uselist=False
    )


class Template(UUIDTimestampMixin, Base):
    """Reusable user-owned generation configuration."""

    __tablename__ = "templates"
    __table_args__ = (Index("ix_templates_user_name", "user_id", "name", unique=True),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    scenario: Mapped[str] = mapped_column(String(100), default="none", nullable=False)
    configuration: Mapped[dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    export_type: Mapped[str] = mapped_column(String(50), default="zip", nullable=False)
    quality: Mapped[dict[str, float]] = mapped_column(JSON, default=dict, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(100), default="Beginner", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user: Mapped[User] = relationship(back_populates="templates")


class SavedDataset(UUIDTimestampMixin, Base):
    """Saved export metadata retained independently from history presentation."""

    __tablename__ = "saved_datasets"
    __table_args__ = (Index("ix_saved_datasets_user_filename", "user_id", "filename"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    history_id: Mapped[UUID] = mapped_column(
        ForeignKey("generation_history.id"), unique=True, nullable=False
    )
    filename: Mapped[str] = mapped_column(String(300), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    history: Mapped[GenerationHistory] = relationship(back_populates="saved_dataset")


class RefreshToken(UUIDTimestampMixin, Base):
    """Refresh-token allowlist entry used for rotation and logout."""

    __tablename__ = "refresh_tokens"
    __table_args__ = (Index("ix_refresh_tokens_user_id", "user_id"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
