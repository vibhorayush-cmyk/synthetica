"""Current-user profile endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.schemas import ProfileUpdateRequest, UserResponse
from app.auth.service import AuthService, AuthenticationError


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser) -> UserResponse:
    """Return the current user profile."""
    return UserResponse.from_model(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: ProfileUpdateRequest, user: CurrentUser, session: DbSession
) -> UserResponse:
    """Update the current user's name, avatar, or password."""
    try:
        updated = await AuthService(session).update_profile(user, payload)
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error
    return UserResponse.from_model(updated)
