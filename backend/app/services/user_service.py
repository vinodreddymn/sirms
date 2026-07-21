from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import hash_password
from app.models.security import User
from app.repositories.security import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def create_user(self, username: str, full_name: str, email: str, password: str) -> User:
        if await self.user_repo.get_by_username(username):
            raise ConflictException("Username already exists")
        if await self.user_repo.get_by_email(email):
            raise ConflictException("Email already exists")
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def list_users(self, offset: int = 0, limit: int = 100) -> tuple[list[User], int]:
        users = await self.user_repo.list(offset=offset, limit=limit)
        total = await self.user_repo.count()
        return users, total

    async def get_user(self, user_id: UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def update_user(self, user_id: UUID, **data: dict) -> User:
        user = await self.get_user(user_id)
        for field, value in data.items():
            if value is not None and hasattr(user, field):
                setattr(user, field, value)
        await self.session.flush()
        return user
