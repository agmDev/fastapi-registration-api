from app.infrastructure.database import db
from app.services.users_service import UsersService
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


def get_users_service() -> UsersService:
    return UsersService(db)



