"""HTTP routes for template management and generation."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.generation import GenerateResponse
from app.templates.repository import JsonTemplateRepository
from app.templates.schemas import TemplateCreate, TemplateResponse, TemplateUpdate
from app.templates.service import TemplateService


router = APIRouter(prefix="/templates", tags=["templates"])


def get_template_service() -> TemplateService:
    """Create a template service with the JSON repository."""
    return TemplateService(JsonTemplateRepository())


@router.get("", response_model=list[TemplateResponse])
async def list_templates(
    service: TemplateService = Depends(get_template_service),
) -> list[TemplateResponse]:
    """Return all templates."""
    return [
        TemplateResponse.from_model(template) for template in service.list_templates()
    ]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str, service: TemplateService = Depends(get_template_service)
) -> TemplateResponse:
    """Return one template by id."""
    try:
        template = service.get_template(template_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    return TemplateResponse.from_model(template)


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateCreate, service: TemplateService = Depends(get_template_service)
) -> TemplateResponse:
    """Create a template."""
    try:
        template = service.create_template(payload)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error
    return TemplateResponse.from_model(template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    payload: TemplateUpdate,
    service: TemplateService = Depends(get_template_service),
) -> TemplateResponse:
    """Update a template."""
    try:
        template = service.update_template(template_id, payload)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    return TemplateResponse.from_model(template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str, service: TemplateService = Depends(get_template_service)
) -> None:
    """Delete a template."""
    service.delete_template(template_id)


@router.post("/generate/from-template/{template_id}", response_model=GenerateResponse)
async def generate_from_template(
    template_id: str,
    request: Request,
    service: TemplateService = Depends(get_template_service),
) -> GenerateResponse:
    """Generate a dataset bundle from a saved template."""
    try:
        generated = service.generate_from_template(template_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error

    download_url = (
        str(
            request.url_for(
                "download_export", filename=Path(generated.download_url).name
            )
        )
        if generated.download_url
        else ""
    )
    return GenerateResponse(
        download_url=download_url,
        generated_files=generated.generated_files,
        row_counts=generated.row_counts,
        generated_at=generated.generated_at,
        scenario=generated.scenario,
        quality=generated.quality,
        challenge_title=generated.challenge_title,
        difficulty=generated.difficulty,
        estimated_time=generated.estimated_time,
        challenge_pdf_url="",
    )
