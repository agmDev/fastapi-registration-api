import aiomysql
import logging

from app.domain.models.user import User


class UsersRepository:
    def __init__(self, conn: aiomysql.Connection):
        self.conn = conn

    async def create(self, email: str, hashed_password: str) -> None:
        async with self.conn.cursor() as cursor:
            row = await cursor.execute(
                """
                INSERT INTO users (email, hashed_password, is_active)
                VALUES (%s, %s, %s)
                """,
                (email, hashed_password, False),
            )
            return cursor.lastrowid


    async def get_by_id(self, id: int) -> User | None:
        async with self.conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT id, email, hashed_password, is_active, created_at FROM users WHERE id = %s",
                (id,),
            )
            row = await cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row["id"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            is_active=row["is_active"],
            created_at=row["created_at"]
        )

    async def get_by_email(self, email: str) -> User | None:
        async with self.conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT id, email, hashed_password, is_active, created_at FROM users WHERE email = %s",
                (email,),
            )
            row = await cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row["id"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            is_active=row["is_active"],
            created_at=row["created_at"]
        )

    async def activate(self, user_id: int) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE users SET is_active=TRUE WHERE id=%s",
                (user_id,)
        )