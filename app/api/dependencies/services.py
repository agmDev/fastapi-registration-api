from fastapi import Depends

from app.infrastructure.database import get_db
from app.services.users_service import UsersService
from app.api.dependencies.email import get_email_client


def get_users_service(email_client=Depends(get_email_client)) -> UsersService:

    return UsersService(get_db(), email_client)
