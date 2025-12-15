from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager

from app.settings import settings
from app.infrastructure.logging import setup_logging
from app.api.router.healthcheck import router as healthcheck_router
from app.api.exception_handlers import register_exception_handlers
from app.api.router.users import router as user_router
from app.api.router.activation import router as activation_router
from app.infrastructure.migrate_db import migrate_database
from app.infrastructure.database import get_db


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting application")
    try:
        db = get_db()
        if settings.environment != "test":
            await db.connect()
            await migrate_database()

        logger.info("application started succesfully")
    except Exception:
        logger.error("Failed to start application:", exc_info=True)
        raise

    yield
    logger.info("Shutting down application...")
    if settings.environment != "test":
        await db.close()
    logger.info("Application shut down successfully")


app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan
)

routers = healthcheck_router, user_router, activation_router
for router in routers:
    app.include_router(router)

register_exception_handlers(app)
