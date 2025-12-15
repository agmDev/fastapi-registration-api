import os

os.environ.setdefault("environment", "test")
os.environ.setdefault("MYSQL_HOST", "localhost")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_USER", "test")
os.environ.setdefault("MYSQL_PASSWORD", "test")
os.environ.setdefault("MYSQL_DATABASE", "test")

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.api.dependencies.services import get_users_service
from app.api.dependencies.auth import get_current_user_id


class FakeUsersService:
    def __init__(self):
        self.register = AsyncMock()
        self.activate = AsyncMock()


@pytest.fixture()
def users_service_mock() -> FakeUsersService:
    return FakeUsersService()


@pytest.fixture()
def client(users_service_mock: FakeUsersService) -> TestClient:
    app.dependency_overrides[get_users_service] = lambda: users_service_mock
    app.dependency_overrides[get_current_user_id] = lambda: 42

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
