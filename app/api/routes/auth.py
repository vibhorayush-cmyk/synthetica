"""Registration, JWT lifecycle, and password-reset endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetTokenResponse,
    RefreshRequest,
    RegistrationRequest,
    RegistrationResponse,
    TokenResponse,
    UserResponse,
)
from app.auth.service import AuthService, AuthenticationError


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegistrationRequest, session: DbSession
) -> RegistrationResponse:
    """Register a user and return tokens for the initial authenticated session."""
    try:
        user, tokens = await AuthService(session).register(payload)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error
    return RegistrationResponse(
        user=UserResponse.from_model(user),
        verification_message="Verification email delivery is mocked; the account is ready to use.",
        tokens=tokens,
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: DbSession) -> TokenResponse:
    """Exchange email and password for short-lived access and refresh tokens."""
    try:
        return await AuthService(session).login(payload)
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        ) from error


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, session: DbSession) -> TokenResponse:
    """Rotate a valid refresh token."""
    try:
        return await AuthService(session).refresh(payload.refresh_token)
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        ) from error


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, user: CurrentUser, session: DbSession) -> None:
    """Revoke the supplied refresh token for the current user."""
    try:
        await AuthService(session).logout(user, payload.refresh_token)
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        ) from error


@router.post("/password-reset/request", response_model=PasswordResetTokenResponse)
async def request_password_reset(
    payload: PasswordResetRequest, session: DbSession
) -> PasswordResetTokenResponse:
    """Return a mocked reset token without exposing whether an email exists."""
    token = await AuthService(session).create_password_reset_token(payload.email)
    return PasswordResetTokenResponse(
        reset_token=token,
        message="If the account exists, a password reset token has been created.",
    )


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_password_reset(
    payload: PasswordResetConfirm, session: DbSession
) -> None:
    """Set a new password using a valid reset token."""
    try:
        await AuthService(session).reset_password(payload)
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        ) from error


@router.get("/me", response_model=UserResponse)
async def current_user(user: CurrentUser) -> UserResponse:
    """Compatibility shortcut for the current authenticated account."""
    return UserResponse.from_model(user)
