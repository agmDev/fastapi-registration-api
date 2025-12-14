from fastapi import Depends

from app.infrastructure.database import db
from app.services.users_service import UsersService
from app.api.dependencies.email import get_email_client


def get_users_service(email_client=Depends(get_email_client)) -> UsersService:

    return UsersService(db, email_client)
