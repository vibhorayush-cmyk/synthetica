"""Authenticated HTTP routes for user-owned generation history."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.history.database_service import AsyncHistoryService
from app.history.schemas import HistoryEntryResponse


router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[HistoryEntryResponse])
async def list_history(user: CurrentUser, session: DbSession) -> list[HistoryEntryResponse]:
    """List the current user's exported datasets only."""
    return await AsyncHistoryService(session).list(user.id)


@router.get("/{entry_id}", response_model=HistoryEntryResponse)
async def get_history_entry(
    entry_id: UUID, user: CurrentUser, session: DbSession
) -> HistoryEntryResponse:
    """Retrieve a history entry owned by the current user."""
    try:
        return await AsyncHistoryService(session).get(entry_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_entry(entry_id: UUID, user: CurrentUser, session: DbSession) -> None:
    """Delete one user-owned history entry."""
    try:
        await AsyncHistoryService(session).delete(entry_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_history(user: CurrentUser, session: DbSession) -> None:
    """Delete all history metadata belonging to the current user."""
    await AsyncHistoryService(session).delete_all(user.id)


@router.post("/{entry_id}/regenerate", response_model=HistoryEntryResponse)
async def regenerate_history_entry(
    entry_id: UUID, user: CurrentUser, session: DbSession
) -> HistoryEntryResponse:
    """Create a user-owned clone that can be used as a regeneration starting point."""
    try:
        return await AsyncHistoryService(session).clone(entry_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("/{entry_id}/clone", response_model=HistoryEntryResponse)
async def clone_history_entry(
    entry_id: UUID, user: CurrentUser, session: DbSession
) -> HistoryEntryResponse:
    """Clone only a record belonging to the current user."""
    try:
        return await AsyncHistoryService(session).clone(entry_id, user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
