"""Dataset generation endpoints."""

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse

from app.config import EXPORTS_DIR
from app.config import settings
from app.core.metrics import metrics
from app.exporters.storage import ExportStorageLimitError
from app.models.generation import GenerateRequest, GenerateResponse
from app.services.generation_service import GenerationService, get_generation_service


router = APIRouter(tags=["generation"])
logger = logging.getLogger(__name__)


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_dataset(
    payload: GenerateRequest,
    request: Request,
    service: GenerationService = Depends(get_generation_service),
) -> GenerateResponse:
    """Generate, export, and describe a dataset bundle."""
    try:
        generated = await asyncio.wait_for(
            asyncio.to_thread(service.generate, payload),
            timeout=settings.generation_timeout_seconds,
        )
    except TimeoutError as error:
        metrics.record_timeout()
        logger.warning(
            "dataset_generation_timed_out",
            extra={
                "industry": payload.industry,
                "scenario": payload.scenario,
                "timeout_seconds": settings.generation_timeout_seconds,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                "Generation timed out after "
                f"{settings.generation_timeout_seconds} seconds. Reduce the dataset size and try again."
            ),
        ) from error
    except ExportStorageLimitError as error:
        logger.warning(
            "dataset_generation_rejected_storage_limit",
            extra={"industry": payload.industry, "scenario": payload.scenario},
        )
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail="Export storage is temporarily full. Please try again later.",
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    zip_path = Path(generated.export.zip_path)
    download_url = str(request.url_for("download_export", filename=zip_path.name))
    bundle_name = Path(generated.export.folder_path).name
    challenge_pdf_url = str(
        request.url_for(
            "download_export_file",
            bundle_name=bundle_name,
            filename="challenge.pdf",
        )
    )
    return GenerateResponse(
        download_url=download_url,
        generated_files=[Path(path).name for path in generated.export.files],
        row_counts={name: len(table) for name, table in generated.tables.items()},
        generated_at=generated.export.generated_at,
        scenario=generated.scenario,
        quality=generated.quality,
        challenge_title=generated.challenge.title,
        difficulty=generated.challenge.difficulty,
        estimated_time=generated.challenge.estimated_completion_time,
        challenge_pdf_url=challenge_pdf_url,
    )


@router.get("/downloads/{bundle_name}/{filename}", name="download_export_file")
async def download_export_file(bundle_name: str, filename: str) -> FileResponse:
    """Return a safe individual artifact from an exported dataset bundle."""
    if (
        Path(bundle_name).name != bundle_name
        or Path(filename).name != filename
        or filename not in {"challenge.pdf"}
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    export_root = EXPORTS_DIR.resolve()
    file_path = (export_root / bundle_name / filename).resolve()
    if export_root not in file_path.parents or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(path=file_path, media_type="application/pdf", filename=filename)


@router.get("/downloads/{filename}", name="download_export")
async def download_export(filename: str) -> FileResponse:
    """Return an exported ZIP archive by file name."""
    if Path(filename).name != filename or not filename.endswith(".zip"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    export_root = EXPORTS_DIR.resolve()
    file_path = (export_root / filename).resolve()
    if file_path.parent != export_root or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return FileResponse(
        path=file_path,
        media_type="application/zip",
        filename=filename,
    )
