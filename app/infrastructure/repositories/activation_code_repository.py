import aiomysql
from datetime import datetime, timezone

from app.domain.models.activation_code import ActivationCode


class ActivationCodeRepository:
    def __init__(self, conn: aiomysql.Connection):
        self._conn = conn

    async def create_or_replace(
        self,
        user_id: int,
        hashed_code: str,
        expires_at: datetime,
    ) -> None:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO activation_codes
                (user_id, hashed_code, expires_at, used)
                VALUES (%s, %s, %s, FALSE)
                ON DUPLICATE KEY UPDATE
                    hashed_code = VALUES(hashed_code),
                    expires_at = VALUES(expires_at),
                    used = FALSE
                """,
                (user_id, hashed_code, expires_at),
            )

    async def get_for_update(self, user_id: int) -> ActivationCode | None:
        async with self._conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT user_id, code, expires_at, used
                FROM activation_codes
                WHERE user_id = %s
                FOR UPDATE
                """,
                (user_id,),
            )
            row = await cursor.fetchone()

            return ActivationCode(
                    user_id=row["user_id"],
                    hashed_code=row["hashed_code"],
                    expires_at=row["expires_at"].replace(tzinfo=timezone.utc),
                    used=row["used"]
                )

    async def mark_used(self, user_id: int) -> None:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE activation_codes
                SET used = TRUE
                WHERE user_id = %s
                """,
                (user_id,),
            )
