from app.domain.models.user import User
from app.infrastructure.database import Database
from app.infrastructure.repositories.users_repository import UsersRepository


class UsersService:
    def __init__(self, db: Database):
        self.db = db

    async def register(self, email: str, password: str) -> User:
        async with self.db.transaction() as conn:
            repo = UsersRepository(conn)
            
            if await repo.get_by_email(email):
                raise ValueError("USER_ALREADY_EXISTS")
            
            return await repo.create(email, password)

    async def activate(self, user: User) -> None:
        if user.is_active:
            repo = UsersRepository(conn)
            async with self.db.transaction() as conn:
                return await repo.activate(user.id)
