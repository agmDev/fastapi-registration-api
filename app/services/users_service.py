from datetime import datetime, timedelta, timezone
import secrets

from app.domain.models.user import User
from app.domain.models.activation_code import ActivationCode
from app.infrastructure.database import Database
from app.infrastructure.repositories.users_repository import UsersRepository
from app.infrastructure.repositories.activation_code_repository import ActivationCodeRepository
from app.domain.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    InvalidActivationCode,
    ActivationCodeExpired,
    UserAlreadyActive
)


ACTIVATION_CODE_TTL = timedelta(minutes=1)

class UsersService:
    def __init__(self, db: Database):
        self.db = db

    def _generate_activation_code(self) -> str:
        return f"{secrets.randbelow(10_000):04d}"

    async def register(self, email: str, password: str) -> User:
        now = datetime.now(tz=timezone.utc)
        async with self.db.transaction() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            codes_repo: ActivationCodeRepository = ActivationCodeRepository(conn)
            
            user = await users_repo.get_by_email(email)
            if user:
                raise UserAlreadyExists()

            user_id = await users_repo.create(email, password) 
            code = self._generate_activation_code()
            expires_at = now + ACTIVATION_CODE_TTL

            await codes_repo.create_or_replace(
                user_id=user_id,
                code=code,
                expires_at=expires_at
            )

            return user

    async def activate(self, user_id: int, code: int) -> None:
        now = datetime.now(tz=timezone.utc)

        async with self.db.transaction() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            codes_repo: ActivationCodeRepository = ActivationCodeRepository(conn)

            user: User = await users_repo.get_by_id(user_id)
            activation_code: ActivationCode = await codes_repo.get_for_update(user_id)

            if not user:
                raise InvalidCredentials()

            if user.is_active:
                raise UserAlreadyActive()

            if activation_code.code != code:
                raise InvalidActivationCode()
            
            if activation_code.expires_at < now:
                raise ActivationCodeExpired()

            await users_repo.activate(user_id)
            await codes_repo.mark_used(user_id)
    
    async def verify_credentials(self, email: str, password: str):
        async with self.db.transaction() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            user = await users_repo.get_by_email(email)
            if not user:
                raise InvalidCredentials

            if password != user.hashed_password:
                raise InvalidCredentials
            return user
