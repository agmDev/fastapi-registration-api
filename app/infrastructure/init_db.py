import aiomysql
import logging
from pathlib import Path

from app.settings import settings

logger = logging.getLogger(__name__)


async def init_database():
    """Initialize database with the schema"""
    logger.info("test")
    try:
        conn = await aiomysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            charset='utf8mb4'
        )

        async with conn.cursor() as cursor:
            await cursor.execute(f"USE {settings.mysql_database}")
            
            schema_path = Path(__file__).parent / "schema.sql"
            schema_sql = schema_path.read_text()
            
            for statement in schema_sql.split(';'):
                if statement.strip():
                    await cursor.execute(statement)
            
            await conn.commit()
            logger.info("Database schema initialized")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise