import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone

from app.services.users_service import UsersService
from app.domain.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    InvalidActivationCode,
    ActivationCodeExpired,
    UserAlreadyActive,
)
from app.domain.models.user import User
from app.domain.models.activation_code import ActivationCode


class FakeSettings:
    activation_code_ttl = timedelta(minutes=1)
    email_from = "no-reply@test.local"


class FakeCursor:
    async def execute(self, *args, **kwargs):
        return None

    async def fetchone(self):
        return None

    async def fetchall(self):
        return []

    @property
    def lastrowid(self):
        return 1

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def cursor(self, *args, **kwargs):
        return FakeCursor()

    async def begin(self):
        return None

    async def commit(self):
        return None

    async def rollback(self):
        return None


class FakeTransaction:
    async def __aenter__(self):
        return FakeConnection()

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeDatabase:
    def transaction(self):
        return FakeTransaction()

    def get_connection(self):
        return FakeTransaction()


@pytest.mark.asyncio
async def test_register_ok(monkeypatch):
    db = FakeDatabase()
    email_client = AsyncMock()
    settings = FakeSettings()

    service = UsersService(
        db=db,
        email_client=email_client,
        settings=settings,
    )

    users_repo = AsyncMock()
    codes_repo = AsyncMock()

    monkeypatch.setattr(
        "app.services.users_service.UsersRepository",
        lambda conn: users_repo
    )
    monkeypatch.setattr(
        "app.services.users_service.ActivationCodeRepository",
        lambda conn: codes_repo
    )

    users_repo.get_by_email.return_value = None
    users_repo.create.return_value = 42

    user_id = await service.register(
        email="test@example.com",
        password="password123",
    )

    assert user_id == 42
    users_repo.get_by_email.assert_awaited_once_with("test@example.com")
    users_repo.create.assert_awaited_once()
    codes_repo.create_or_replace.assert_awaited_once()
    email_client.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_user_already_exists(monkeypatch):
    db = FakeDatabase()
    email_client = AsyncMock()
    settings = FakeSettings()

    service = UsersService(db, email_client, settings)

    users_repo = AsyncMock()
    monkeypatch.setattr(
        "app.services.users_service.UsersRepository",
        lambda conn: users_repo
    )

    users_repo.get_by_email.return_value = MagicMock()

    with pytest.raises(UserAlreadyExists):
        await service.register(
            email="test@example.com",
            password="password123",
        )

    email_client.send.assert_not_called()


@pytest.mark.asyncio
async def test_activate_ok(monkeypatch):
    db = FakeDatabase()
    settings = FakeSettings()
    service = UsersService(db, AsyncMock(), settings)

    users_repo = AsyncMock()
    codes_repo = AsyncMock()

    monkeypatch.setattr(
        "app.services.users_service.UsersRepository",
        lambda conn: users_repo
    )
    monkeypatch.setattr(
        "app.services.users_service.ActivationCodeRepository",
        lambda conn: codes_repo
    )

    users_repo.get_by_id.return_value = User(
        id=1,
        email="test@example.com",
        hashed_password="hash",
        is_active=False,
        created_at=datetime.now(tz=timezone.utc),
    )

    code = "1234"
    codes_repo.get_for_update.return_value = ActivationCode(
        user_id=1,
        hashed_code=service._hash_activation_code(code),
        expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=1),
        used=False,
    )

    await service.activate(user_id=1, code=code)

    users_repo.activate.assert_awaited_once_with(1)
    codes_repo.mark_used.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_activate_user_already_active(monkeypatch):
    db = FakeDatabase()
    settings = FakeSettings()
    service = UsersService(db, AsyncMock(), settings)

    users_repo = AsyncMock()
    monkeypatch.setattr(
        "app.services.users_service.UsersRepository",
        lambda conn: users_repo
    )

    users_repo.get_by_id.return_value = User(
        id=1,
        email="test@example.com",
        hashed_password="hash",
        is_active=True,
        created_at=datetime.now(tz=timezone.utc),
    )

    with pytest.raises(UserAlreadyActive):
        await service.activate(1, "1234")


@pytest.mark.asyncio
async def test_activate_invalid_code(monkeypatch):
    db = FakeDatabase()
    settings = FakeSettings()
    service = UsersService(db, AsyncMock(), settings)

    users_repo = AsyncMock()
    codes_repo = AsyncMock()

    monkeypatch.setattr(
        "app.services.users_service.UsersRepository",
        lambda conn: users_repo
    )
    monkeypatch.setattr(
        "app.services.users_service.ActivationCodeRepository",
        lambda conn: codes_repo
    )

    users_repo.get_by_id.return_value = User(
        id=1,
        email="test@example.com",
        hashed_password="hash",
        is_active=False,
        created_at=datetime.now(tz=timezone.utc),
    )

    codes_repo.get_for_update.return_value = None

    with pytest.raises(InvalidActivationCode):
        await service.activate(1, "1234")


@pytest.mark.asyncio
async def test_activate_expired_code(monkeypatch):
    db = FakeDatabase()
    settings = FakeSettings()
    service = UsersService(db, AsyncMock(), settings)

    users_repo = AsyncMock()
    codes_repo = AsyncMock()

    monkeypatch.setattr(
        "app.services.users_service.UsersRepository",
        lambda conn: users_repo
    )
    monkeypatch.setattr(
        "app.services.users_service.ActivationCodeRepository",
        lambda conn: codes_repo
    )

    users_repo.get_by_id.return_value = User(
        id=1,
        email="test@example.com",
        hashed_password="hash",
        is_active=False,
        created_at=datetime.now(tz=timezone.utc),
    )

    codes_repo.get_for_update.return_value = ActivationCode(
        user_id=1,
        hashed_code=service._hash_activation_code("1234"),
        expires_at=datetime.now(tz=timezone.utc) - timedelta(minutes=1),
        used=False,
    )

    with pytest.raises(ActivationCodeExpired):
        await service.activate(1, "1234")


@pytest.mark.asyncio
async def test_verify_credentials_ok(monkeypatch):
    db = FakeDatabase()
    settings = FakeSettings()
    service = UsersService(db, AsyncMock(), settings)

    users_repo = AsyncMock()
    monkeypatch.setattr(
        "app.services.users_service.UsersRepository",
        lambda conn: users_repo
    )

    users_repo.get_by_email.return_value = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed",
        is_active=True,
        created_at=datetime.now(tz=timezone.utc),
    )

    monkeypatch.setattr(
        "app.services.users_service.verify_password",
        lambda plain, hashed: True
    )

    user_id = await service.verify_credentials(
        "test@example.com",
        "password"
    )

    assert user_id == 1
