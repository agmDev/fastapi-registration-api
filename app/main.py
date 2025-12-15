from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager

from app.settings import AppSettings
from app.infrastructure.logging import setup_logging
from app.api.router.healthcheck import router as healthcheck_router
from app.api.exception_handlers import register_exception_handlers
from app.api.router.users import router as user_router
from app.api.router.activation import router as activation_router
from app.infrastructure.migrate_db import migrate_database
from app.infrastructure.database import Database


def create_app(settings: AppSettings | None = None) -> FastAPI:
    setup_logging()
    logger = logging.getLogger(__name__)

    if settings is None:
        settings = AppSettings()

    database = Database(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("starting application")

        await database.connect()
        if settings.environment != "test":
            await migrate_database()

        app.state.db = database

        yield

        logger.info("shutting down application")
        await database.disconnect()

    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
        lifespan=lifespan,
    )

    for router in (healthcheck_router, user_router, activation_router):
        app.include_router(router)

    register_exception_handlers(app)

    return app
