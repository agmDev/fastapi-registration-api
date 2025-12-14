from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager

from app.settings import settings
from app.api.router.healthcheck import router as healthcheck_router
from app.api.router.users import router as user_router
from app.api.router.activation import router as activation_router
from app.infrastructure.init_db import init_database


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting application")
    try:
        await init_database()

        routers = healthcheck_router, user_router, activation_router
        for router in routers:
            app.include_router(router)
        logger.info("application started succesfully")
    except:
        logger.error(f"Failed to start application:", exc_info=True)
        raise

    yield


app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan
)