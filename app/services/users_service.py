from datetime import datetime, timedelta
import secrets

from app.domain.models.user import User
from app.infrastructure.database import Database
from app.infrastructure.repositories.users_repository import UsersRepository
from app.infrastructure.repositories.activation_code_repository import ActivationCodeRepository

ACTIVATION_CODE_TTL = timedelta(minutes=1)

class UsersService:
    def __init__(self, db: Database):
        self.db = db

    def _generate_activation_code(self) -> str:
        return f"{secrets.randbelow(10_000):04d}"

    async def register(self, email: str, password: str) -> User:
        async with self.db.transaction() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            codes_repo: ActivationCodeRepository = ActivationCodeRepository(conn)
            
            user = await users_repo.get_by_email(email)
            if user:
                raise ValueError("USER_ALREADY_EXISTS")
            user_id = await users_repo.create(email, password) 
            code = self._generate_activation_code()
            expires_at = datetime.now() + ACTIVATION_CODE_TTL

            await codes_repo.create_or_replace(
                user_id=user_id,
                code=code,
                expires_at=expires_at
            )

            return user

    async def activate(self, user_id: int, code: int) -> None:
        async with self.db.transaction() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            codes_repo: ActivationCodeRepository = ActivationCodeRepository(conn)

            user = await users_repo.get_by_id(user_id)
            activation = await codes_repo.get_for_update(user_id)

            await users_repo.activate(user_id)
            await codes_repo.mark_used(user_id)
    
    async def verify_credentials(self, email: str, password: str):
        async with self.db.transaction() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            user = await users_repo.get_by_email(email)
            if not user:
                raise ValueError("Invalid Creds")

            if password != user.hashed_password:
                raise ValueError("Invalid Creds")
            return user
