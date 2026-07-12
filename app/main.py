"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import EXPORTS_DIR, settings
from app.core.logging import configure_logging
from app.core.middleware import RateLimitMiddleware, RequestContextMiddleware
from app.core.metrics import metrics
from app.db.session import dispose_engine
from app.exporters.storage import ExportStorageManager
from app.db.session import dispose_engine


EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepare runtime directories when the application starts."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    maintenance = ExportStorageManager(
        EXPORTS_DIR,
        settings.export_ttl_hours,
        settings.max_export_storage_mb,
    ).maintain()
    metrics.record_storage_maintenance(
        maintenance.expired_entries_removed,
        maintenance.capacity_entries_removed,
        maintenance.usage_bytes,
    )
    try:
        yield
    finally:
        await dispose_engine()
    await dispose_engine()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_strings,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)
app.add_middleware(RateLimitMiddleware, settings=settings)
app.add_middleware(RequestContextMiddleware)

app.include_router(api_router)
app.include_router(api_router, prefix=settings.api_v1_prefix)
