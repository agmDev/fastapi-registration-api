import os
import pytest
import pymysql
from testcontainers.mysql import MySqlContainer
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def mysql_container():
    """
    MySQL éphémère pour les tests d’intégration
    """
    container = MySqlContainer(
        image="mysql:8.0",
        username="test",
        password="test",
        dbname="test_db",
    )
    container.start()
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="session", autouse=True)
def integration_env(mysql_container):
    """
    Variables d’environnement pour l’intégration
    (avant toute création d’app)
    """
    os.environ["ENVIRONMENT"] = "integration"
    os.environ["MYSQL_HOST"] = mysql_container.get_container_host_ip()
    os.environ["MYSQL_PORT"] = str(mysql_container.get_exposed_port(3306))
    os.environ["MYSQL_USER"] = mysql_container.username
    os.environ["MYSQL_PASSWORD"] = mysql_container.password
    os.environ["MYSQL_DATABASE"] = mysql_container.dbname


@pytest.fixture(scope="session", autouse=True)
def init_schema(integration_env):
    """
    Initialisation du schéma SQL
    """
    conn = pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )

    with conn.cursor() as cursor:
        with open("app/infrastructure/schema.sql") as f:
            sql = f.read()

        for statement in filter(None, map(str.strip, sql.split(";"))):
            cursor.execute(statement)

    conn.commit()
    conn.close()


@pytest.fixture(scope="session")
def client(integration_env):
    """
    App FastAPI réelle, créée via la factory
    """
    from app.main import create_app
    from app.settings import AppSettings

    app = create_app(AppSettings())

    with TestClient(app) as client:
        yield client
