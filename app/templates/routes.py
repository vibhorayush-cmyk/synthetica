"""Authenticated routes for user-owned dataset templates."""

import asyncio
from pathlib import Path
from time import perf_counter
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from app.auth.dependencies import CurrentUser, DbSession
from app.history.database_service import AsyncHistoryService
from app.models.generation import GenerateResponse
from app.services.generation_service import get_generation_service
from app.templates.database_service import AsyncTemplateService
from app.templates.schemas import TemplateCreate, TemplateResponse, TemplateUpdate


router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateResponse])
async def list_templates(user: CurrentUser, session: DbSession) -> list[TemplateResponse]:
    return await AsyncTemplateService(session).list(user.id)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: UUID, user: CurrentUser, session: DbSession) -> TemplateResponse:
    try:
        return await AsyncTemplateService(session).get(template_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateCreate, user: CurrentUser, session: DbSession
) -> TemplateResponse:
    try:
        return await AsyncTemplateService(session).create(user.id, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID, payload: TemplateUpdate, user: CurrentUser, session: DbSession
) -> TemplateResponse:
    try:
        return await AsyncTemplateService(session).update(template_id, user.id, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: UUID, user: CurrentUser, session: DbSession) -> None:
    try:
        await AsyncTemplateService(session).delete(template_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("/generate/from-template/{template_id}", response_model=GenerateResponse)
async def generate_from_template(
    template_id: UUID, request: Request, user: CurrentUser, session: DbSession
) -> GenerateResponse:
    """Generate a user-owned dataset from one of the user's templates."""
    started = perf_counter()
    service = AsyncTemplateService(session)
    try:
        payload = await service.generate_request(template_id, user.id)
        generated = await asyncio.to_thread(get_generation_service().generate, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    response = GenerateResponse(
        download_url=str(
            request.url_for(
                "download_export", filename=Path(generated.export.zip_path).name
            )
        ),
        generated_files=[Path(path).name for path in generated.export.files],
        row_counts={name: len(table) for name, table in generated.tables.items()},
        generated_at=generated.export.generated_at,
        scenario=generated.scenario,
        quality=generated.quality,
        challenge_title=generated.challenge.title,
        difficulty=generated.challenge.difficulty,
        estimated_time=generated.challenge.estimated_completion_time,
        challenge_pdf_url=str(
            request.url_for(
                "download_export_file",
                bundle_name=Path(generated.export.folder_path).name,
                filename="challenge.pdf",
            )
        ),
    )
    await AsyncHistoryService(session).record_generation(
        user.id, payload, response, int((perf_counter() - started) * 1000)
    )
    return response
