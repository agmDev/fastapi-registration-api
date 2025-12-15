import os
import pymysql
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import AppSettings


@pytest.fixture(scope="session")
def settings():
    os.environ["environment"] = "integration"
    return AppSettings()


@pytest.fixture(scope="session")
def app(settings):
    app = create_app(settings)
    return app


@pytest.fixture(scope="session")
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def clean_database(settings):
    if settings.environment != "integration":
        raise RuntimeError("Refusing to clean database outside integration environment")

    conn = pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        autocommit=True,
    )

    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE activation_codes;")
        cursor.execute("TRUNCATE TABLE users;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    conn.close()