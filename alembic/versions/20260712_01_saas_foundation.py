"""Create SaaS authentication and user-owned data tables.

Revision ID: 20260712_01
Revises:
Create Date: 2026-07-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260712_01"
down_revision = None
branch_labels = None
depends_on = None


def _audit_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=2048)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
        *_audit_columns(),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table(
        "generation_history",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("dataset_name", sa.String(length=200), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=False),
        sa.Column("scenario", sa.String(length=100), nullable=False, server_default="none"),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("quality", sa.JSON(), nullable=False),
        sa.Column("export_type", sa.String(length=50), nullable=False, server_default="zip"),
        sa.Column("download_filename", sa.String(length=300), nullable=False),
        sa.Column("dataset_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="completed"),
        sa.Column("generation_duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("challenge_title", sa.String(length=300)),
        sa.Column("generated_files", sa.JSON(), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_generation_history_user_id", "generation_history", ["user_id"])
    op.create_index("ix_generation_history_industry", "generation_history", ["industry"])
    op.create_index("ix_generation_history_user_generated", "generation_history", ["user_id", "generated_at"])
    op.create_index("ix_generation_history_status", "generation_history", ["status"])
    op.create_table(
        "templates",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("industry", sa.String(length=100), nullable=False),
        sa.Column("scenario", sa.String(length=100), nullable=False, server_default="none"),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("export_type", sa.String(length=50), nullable=False, server_default="zip"),
        sa.Column("quality", sa.JSON(), nullable=False),
        sa.Column("difficulty", sa.String(length=100), nullable=False, server_default="Beginner"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        *_audit_columns(),
    )
    op.create_index("ix_templates_user_id", "templates", ["user_id"])
    op.create_index("ix_templates_user_name", "templates", ["user_id", "name"], unique=True)
    op.create_table(
        "saved_datasets",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("history_id", sa.Uuid(), sa.ForeignKey("generation_history.id"), nullable=False),
        sa.Column("filename", sa.String(length=300), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        *_audit_columns(),
        sa.UniqueConstraint("history_id"),
    )
    op.create_index("ix_saved_datasets_user_id", "saved_datasets", ["user_id"])
    op.create_index("ix_saved_datasets_user_filename", "saved_datasets", ["user_id", "filename"])
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_id", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        *_audit_columns(),
        sa.UniqueConstraint("token_id"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_id", "refresh_tokens", ["token_id"])


def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_table("saved_datasets")
    op.drop_table("templates")
    op.drop_table("generation_history")
    op.drop_table("users")
