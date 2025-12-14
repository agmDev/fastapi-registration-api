import aiomysql
from contextlib import asynccontextmanager
from typing import AsyncIterator
import logging

from app.settings import settings

logger = logging.getLogger(__name__)


class Database:
    """Handles MySQL connexion pool"""

    def __init__(self):
        self.pool: aiomysql.Pool | None = None

    async def connect(self):
        """Initialize connexion pool """
        try:
            self.pool = await aiomysql.create_pool(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                db=settings.mysql_database,
                minsize=settings.db_pool_min_size,
                maxsize=settings.db_pool_max_size,
                autocommit=False,
                charset='utf8mb4'
            )
            logger.info("Database pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise

    async def disconnect(self):
        """Close the connexion pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("Database pool closed")

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[aiomysql.Connection]:
        """Context manager to obtain a connexion from pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[aiomysql.Connection]:
        """Context manager for transaction"""
        async with self.get_connection() as conn:
            try:
                await conn.begin()
                yield conn
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise


db = Database()
