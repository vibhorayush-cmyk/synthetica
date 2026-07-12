"""Validated authentication and profile API payloads."""

from datetime import datetime
import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models import User


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class RegistrationRequest(BaseModel):
    """New-account input with deliberate password-strength checks."""

    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=2, max_length=160)
    email: str = Field(max_length=320)
    password: str = Field(min_length=12, max_length=72)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        email = value.strip().lower()
        if not EMAIL_PATTERN.fullmatch(email):
            raise ValueError("email must be a valid email address")
        return email

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if not re.search(r"[a-z]", value):
            raise ValueError("password must include a lowercase letter")
        if not re.search(r"[A-Z]", value):
            raise ValueError("password must include an uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("password must include a number")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=320)
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: str = Field(max_length=320)


class PasswordResetConfirm(BaseModel):
    token: str
    password: str = Field(min_length=12, max_length=72)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        return RegistrationRequest.strong_password(value)


class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    avatar_url: str | None = Field(default=None, max_length=2048)
    current_password: str | None = Field(default=None, min_length=1, max_length=72)
    password: str | None = Field(default=None, min_length=12, max_length=72)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str | None) -> str | None:
        if value is not None:
            return RegistrationRequest.strong_password(value)
        return value


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class RegistrationResponse(BaseModel):
    user: UserResponse
    verification_message: str
    tokens: TokenResponse


class PasswordResetTokenResponse(BaseModel):
    reset_token: str
    message: str
