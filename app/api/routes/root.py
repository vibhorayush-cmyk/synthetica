"""Root endpoint."""

from fastapi import APIRouter


router = APIRouter(tags=["service"])


@router.get("/")
async def root() -> dict[str, str]:
    """Return basic service information."""
    return {"service": "synthetic-analytics-data-generator", "status": "ready"}
