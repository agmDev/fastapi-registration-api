from app.infrastructure.database import db
from app.services.users_service import UsersService


def get_users_service() -> UsersService:
    return UsersService(db)
