import aiomysql
from contextlib import asynccontextmanager
from typing import AsyncIterator
import logging

from app.settings import AppSettings


logger = logging.getLogger(__name__)


class Database:
    """Handles MySQL connection pool"""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.pool: aiomysql.Pool | None = None

    async def connect(self):
        if self.settings.environment == "test":
            logger.info("Database connection disabled for test environment")
            return

        self.pool = await aiomysql.create_pool(
            host=self.settings.mysql_host,
            port=self.settings.mysql_port,
            user=self.settings.mysql_user,
            password=self.settings.mysql_password,
            db=self.settings.mysql_database,
            minsize=self.settings.db_pool_min_size,
            maxsize=self.settings.db_pool_max_size,
            autocommit=False,
            charset="utf8mb4",
        )

        logger.info("Database pool created successfully")

    async def disconnect(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("Database pool closed")

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[aiomysql.Connection]:
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[aiomysql.Connection]:
        async with self.get_connection() as conn:
            try:
                await conn.begin()
                yield conn
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise
