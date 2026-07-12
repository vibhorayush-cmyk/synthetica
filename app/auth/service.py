"""JWT and user-account application service."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import bcrypt
import jwt
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    LoginRequest,
    PasswordResetConfirm,
    ProfileUpdateRequest,
    RegistrationRequest,
    TokenResponse,
)
from app.core.settings import Settings, get_settings
from app.db.models import RefreshToken, User
from app.db.repositories import RefreshTokenRepository, UserRepository


class AuthenticationError(ValueError):
    """Raised for invalid or expired credentials without leaking account state."""


class AuthService:
    """Register users, issue JWTs, and maintain refresh-token rotation."""

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self._users = UserRepository(session)
        self._refresh_tokens = RefreshTokenRepository(session)
        self._settings = settings or get_settings()

    async def register(self, payload: RegistrationRequest) -> tuple[User, TokenResponse]:
        if await self._users.get_by_email(payload.email):
            raise ValueError("an account with this email already exists")
        user = User(
            full_name=payload.full_name.strip(),
            email=payload.email,
            password_hash=self.hash_password(payload.password),
        )
        user = await self._users.create(user)
        return user, await self.issue_tokens(user)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self._users.get_by_email(payload.email.strip().lower())
        if not user or not self.verify_password(payload.password, user.password_hash):
            raise AuthenticationError("invalid email or password")
        if not user.is_active:
            raise AuthenticationError("this account is inactive")
        return await self.issue_tokens(user)

    async def issue_tokens(self, user: User) -> TokenResponse:
        now = datetime.now(UTC)
        access_expires = now + timedelta(minutes=self._settings.access_token_expire_minutes)
        refresh_expires = now + timedelta(days=self._settings.refresh_token_expire_days)
        refresh_id = uuid4().hex
        access_token = self._encode(
            {
                "sub": str(user.id),
                "type": "access",
                "role": user.role,
                "jti": uuid4().hex,
                "exp": access_expires,
            }
        )
        refresh_token = self._encode(
            {"sub": str(user.id), "type": "refresh", "jti": refresh_id, "exp": refresh_expires}
        )
        await self._refresh_tokens.create(
            RefreshToken(user_id=user.id, token_id=refresh_id, expires_at=refresh_expires)
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        claims = self.decode(refresh_token, "refresh")
        token = await self._refresh_tokens.get_active(str(claims.get("jti", "")))
        expires_at = token.expires_at.replace(tzinfo=UTC) if token else None
        if not token or expires_at <= datetime.now(UTC):
            raise AuthenticationError("refresh token is invalid or expired")
        user = await self._users.get(UUID(str(claims["sub"])))
        if not user or not user.is_active:
            raise AuthenticationError("refresh token is invalid or expired")
        await self._refresh_tokens.revoke(token, datetime.now(UTC))
        return await self.issue_tokens(user)

    async def logout(self, user: User, refresh_token: str) -> None:
        claims = self.decode(refresh_token, "refresh")
        if claims.get("sub") != str(user.id):
            raise AuthenticationError("refresh token does not belong to this user")
        token = await self._refresh_tokens.get_active(str(claims.get("jti", "")))
        if token:
            await self._refresh_tokens.revoke(token, datetime.now(UTC))

    async def update_profile(self, user: User, payload: ProfileUpdateRequest) -> User:
        if payload.password is not None:
            if not payload.current_password or not self.verify_password(
                payload.current_password, user.password_hash
            ):
                raise AuthenticationError("current password is incorrect")
            user.password_hash = self.hash_password(payload.password)
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url or None
        return await self._users.save(user)

    async def create_password_reset_token(self, email: str) -> str:
        user = await self._users.get_by_email(email.strip().lower())
        # Intentionally return a generic response upstream. The token is a mocked delivery.
        if not user:
            return ""
        expires = datetime.now(UTC) + timedelta(
            minutes=self._settings.password_reset_expire_minutes
        )
        return self._encode({"sub": str(user.id), "type": "reset", "exp": expires})

    async def reset_password(self, payload: PasswordResetConfirm) -> None:
        claims = self.decode(payload.token, "reset")
        user = await self._users.get(UUID(str(claims["sub"])))
        if not user or not user.is_active:
            raise AuthenticationError("password reset token is invalid or expired")
        user.password_hash = self.hash_password(payload.password)
        await self._users.save(user)

    def decode(self, token: str, expected_type: str) -> dict[str, object]:
        try:
            claims = jwt.decode(
                token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm]
            )
        except InvalidTokenError as error:
            raise AuthenticationError("token is invalid or expired") from error
        if claims.get("type") != expected_type or not claims.get("sub"):
            raise AuthenticationError("token is invalid or expired")
        return claims

    def _encode(self, claims: dict[str, object]) -> str:
        return jwt.encode(claims, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except ValueError:
            return False
