from fastapi import Depends, Request

from app.services.users_service import UsersService
from app.api.dependencies.email import get_email_client
from app.api.dependencies.database import get_db
from app.settings import get_settings


def get_users_service(request: Request,
                      email_client=Depends(get_email_client)
                      ) -> UsersService:
    return UsersService(get_db(request), email_client, get_settings())
