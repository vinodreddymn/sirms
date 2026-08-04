from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.security import RefreshToken, User
from app.repositories.security import RefreshTokenRepository, UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.refresh_repo = RefreshTokenRepository(session)
        from app.repositories.security import LoginHistoryRepository
        self.login_history_repo = LoginHistoryRepository(session)

    async def authenticate(self, username: str, password: str, request=None) -> User:
        user = await self.user_repo.get_by_username(username)
        from app.models.security import LoginHistory
        ip_address = request.client.host if request and request.client else None
        device_info = request.headers.get("user-agent") if request else None

        if not user or not verify_password(password, user.password_hash):
            if user:
                history = LoginHistory(
                    user_id=user.id,
                    login_status="FAILED",
                    ip_address=ip_address,
                    device_info=device_info,
                    remarks="Invalid password"
                )
                await self.login_history_repo.create(history)
            raise UnauthorizedException("Invalid username or password")
        if user.is_locked:
            history = LoginHistory(
                user_id=user.id,
                login_status="FAILED",
                ip_address=ip_address,
                device_info=device_info,
                remarks="Account is locked"
            )
            await self.login_history_repo.create(history)
            raise UnauthorizedException("Account is locked")
        history = LoginHistory(
            user_id=user.id,
            login_status="SUCCESS",
            ip_address=ip_address,
            device_info=device_info,
            remarks="Login successful"
        )
        await self.login_history_repo.create(history)
        await self.user_repo.update_last_login(user)
        return user

    async def create_tokens(self, user: User) -> dict[str, str | int]:
        # include is_admin claim when user has ADMIN role
        role_codes = await self.user_repo.get_role_codes(user.id)
        is_admin = any(code == "ADMIN" for code in role_codes)
        access_token = create_access_token(str(user.id), {"role": "user", "is_admin": is_admin})
        refresh_token = create_refresh_token(str(user.id), {"token_id": str(uuid4())})
        refresh = RefreshToken(
            user_id=user.id,
            token_hash=hash_password(refresh_token),
            expires_at=datetime.utcnow() + timedelta(days=30),
            device_info=None,
            ip_address=None,
        )
        await self.refresh_repo.create(refresh)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 1800,
        }

    async def refresh_tokens(self, refresh_token: str) -> dict[str, str | int]:
        payload = self._decode_refresh_token(refresh_token)
        user_id = payload.get("sub")
        token_id = payload.get("token_id")
        if not user_id or not token_id:
            raise UnauthorizedException("Invalid refresh token")

        refresh = await self.refresh_repo.get_active_by_user_and_token(UUID(user_id), refresh_token)
        if not refresh:
            raise UnauthorizedException("Invalid refresh token")

        # include is_admin claim on refreshed access token
        role_codes = await self.user_repo.get_role_codes(UUID(user_id))
        is_admin = any(code == "ADMIN" for code in role_codes)
        access_token = create_access_token(str(user_id), {"role": "user", "is_admin": is_admin})
        new_refresh_token = create_refresh_token(str(user_id), {"token_id": str(uuid4())})
        await self.refresh_repo.revoke(refresh)
        await self.refresh_repo.create(
            RefreshToken(
                user_id=refresh.user_id,
                token_hash=hash_password(new_refresh_token),
                expires_at=datetime.utcnow() + timedelta(days=30),
                device_info=refresh.device_info,
                ip_address=refresh.ip_address,
            )
        )
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "expires_in": 1800,
        }

    async def logout(self, refresh_token: str) -> None:
        payload = self._decode_refresh_token(refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")
        refresh = await self.refresh_repo.get_active_by_user_and_token(UUID(user_id), refresh_token)
        if not refresh:
            raise UnauthorizedException("Invalid refresh token")
        await self.refresh_repo.revoke(refresh)

    async def logout_all(self, user: User) -> None:
        await self.refresh_repo.revoke_all_for_user(user.id)

    async def change_password(self, user: User, old_password: str, new_password: str) -> None:
        if not verify_password(old_password, user.password_hash):
            raise UnauthorizedException("Invalid current password")
        await self.user_repo.update_password_hash(user, hash_password(new_password))
        user.password_changed_at = datetime.utcnow()
        await self.refresh_repo.revoke_all_for_user(user.id)

    def _decode_refresh_token(self, token: str) -> dict[str, str]:
        from app.core.security import decode_token

        return decode_token(token)
