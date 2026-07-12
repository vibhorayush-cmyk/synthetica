"""Async database session dependency."""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import get_settings


def _async_database_url(database_url: str) -> str:
    """Normalize a development SQLite URL to SQLAlchemy's async dialect."""
    if database_url.startswith("sqlite:///") and not database_url.startswith(
        "sqlite+aiosqlite:///"
    ):
        return database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


@lru_cache
def get_engine() -> AsyncEngine:
    """Create one async engine per process."""
    return create_async_engine(
        _async_database_url(get_settings().database_url), pool_pre_ping=True
    )


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create reusable async sessions with explicit transaction boundaries."""
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped async session."""
    async with get_session_factory()() as session:
        yield session


async def dispose_engine() -> None:
    """Close active connection pools during application shutdown."""
    if get_engine.cache_info().currsize:
        await get_engine().dispose()
        get_session_factory.cache_clear()
        get_engine.cache_clear()
