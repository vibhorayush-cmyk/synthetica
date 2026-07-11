"""HTTP routes for generation history."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.history.repository import JsonHistoryRepository
from app.history.schemas import HistoryEntryResponse
from app.history.service import HistoryService


router = APIRouter(prefix="/history", tags=["history"])


def get_history_service() -> HistoryService:
    return HistoryService(JsonHistoryRepository())


@router.get("", response_model=list[HistoryEntryResponse])
async def list_history(
    service: HistoryService = Depends(get_history_service),
) -> list[HistoryEntryResponse]:
    return [HistoryEntryResponse.from_model(entry) for entry in service.list_history()]


@router.get("/{entry_id}", response_model=HistoryEntryResponse)
async def get_history_entry(
    entry_id: str, service: HistoryService = Depends(get_history_service)
) -> HistoryEntryResponse:
    try:
        entry = service.get_history_entry(entry_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    return HistoryEntryResponse.from_model(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_entry(
    entry_id: str, service: HistoryService = Depends(get_history_service)
) -> None:
    service.delete_history_entry(entry_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_history(
    service: HistoryService = Depends(get_history_service),
) -> None:
    service.delete_all_history()


@router.post("/{entry_id}/regenerate", response_model=HistoryEntryResponse)
async def regenerate_history_entry(
    entry_id: str, service: HistoryService = Depends(get_history_service)
) -> HistoryEntryResponse:
    entry = service.clone(entry_id)
    return HistoryEntryResponse.from_model(entry)


@router.post("/{entry_id}/clone", response_model=HistoryEntryResponse)
async def clone_history_entry(
    entry_id: str, service: HistoryService = Depends(get_history_service)
) -> HistoryEntryResponse:
    entry = service.clone(entry_id)
    return HistoryEntryResponse.from_model(entry)
