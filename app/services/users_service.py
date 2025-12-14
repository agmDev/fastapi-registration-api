from datetime import datetime, timezone
from hashlib import sha256
from typing import Optional
import secrets

from app.settings import settings
from app.domain.security import hash_password, verify_password
from app.domain.models.user import User
from app.domain.models.activation_code import ActivationCode
from app.infrastructure.email.client import EmailMessage
from app.infrastructure.database import Database
from app.infrastructure.repositories.users_repository import UsersRepository
from app.infrastructure.repositories.activation_code_repository import (
    ActivationCodeRepository
)
from app.domain.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    InvalidActivationCode,
    ActivationCodeExpired,
    UserAlreadyActive
)


class UsersService:
    def __init__(self, db: Database, email_client):
        self.db = db
        self.email_client = email_client

    def _generate_activation_code(self) -> str:
        return f"{secrets.randbelow(10_000):04d}"

    def _hash_activation_code(self, code: str) -> str:
        return sha256(code.encode()).hexdigest()

    async def register(self, email: str, password: str) -> int:
        now = datetime.now(tz=timezone.utc)
        async with self.db.transaction() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            codes_repo: ActivationCodeRepository = ActivationCodeRepository(conn)

            user = await users_repo.get_by_email(email)
            if user:
                raise UserAlreadyExists()

            user_id = await users_repo.create(email, hash_password(password))
            code = self._generate_activation_code()
            hashed_code = self._hash_activation_code(code)
            expires_at = now + settings.activation_code_ttl

            await codes_repo.create_or_replace(
                user_id=user_id,
                hashed_code=hashed_code,
                expires_at=expires_at
            )

            await self.email_client.send(
                EmailMessage(
                    to=email,
                    sender=settings.email_from,
                    subject="Activate your account",
                    body=f"Your activation code is: {code} (valid for 1 minute)",
                )
            )
            return user_id

    async def activate(self, user_id: int, code: str) -> None:
        now = datetime.now(tz=timezone.utc)

        async with self.db.transaction() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            codes_repo: ActivationCodeRepository = ActivationCodeRepository(
                conn
            )

            user: Optional[User] = await users_repo.get_by_id(user_id)
            activation_code: Optional[ActivationCode] = await codes_repo.get_for_update(user_id)

            if not user:
                raise InvalidCredentials()

            if user.is_active:
                raise UserAlreadyActive()

            if not activation_code:
                raise InvalidActivationCode()

            if activation_code.hashed_code != self._hash_activation_code(code):
                raise InvalidActivationCode()

            if activation_code.expires_at < now:
                raise ActivationCodeExpired()

            await users_repo.activate(user_id)
            await codes_repo.mark_used(user_id)

    async def verify_credentials(self, email: str, password: str):
        async with self.db.get_connection() as conn:
            users_repo: UsersRepository = UsersRepository(conn)
            user = await users_repo.get_by_email(email)
        if not user:
            raise InvalidCredentials()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials()
        return user.id
