"""Health check endpoint."""

from fastapi import APIRouter

from app.config import EXPORTS_DIR
from app.core.metrics import metrics
from app.plugins.registry import create_default_plugin_registry


router = APIRouter(tags=["service"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Report application liveness."""
    return {"status": "healthy"}


@router.get("/ready", tags=["service"])
async def readiness_check() -> dict[str, str]:
    """Report whether required local runtime dependencies are available."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return {"status": "ready"}


@router.get("/readyz", tags=["service"], include_in_schema=False)
async def readiness_probe() -> dict[str, str]:
    """Compatibility alias for common Kubernetes readiness probe naming."""
    return await readiness_check()


@router.get("/metrics", tags=["service"])
async def generation_metrics() -> dict[str, float | int | str]:
    """Expose lightweight generation statistics for monitoring."""
    snapshot = metrics.snapshot()
    snapshot.update(
        {
            "service": "synthetic-analytics-data-generator",
            "requests": snapshot["generation_count"],
            "plugins": len(create_default_plugin_registry().list_ids()),
        }
    )
    return snapshot
