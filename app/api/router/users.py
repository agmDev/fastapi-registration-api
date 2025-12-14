from fastapi import APIRouter, HTTPException, status, Depends

from app.api.dependencies.services import get_users_service
from app.services.users_service import UsersService
from app.api.models.user import (
    UserCreateRequest,
    UserCreateResponse,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: UserCreateRequest,
    service: UsersService = Depends(get_users_service)
) -> UserCreateResponse:
    """
    Create a new user and send an activation code by email.
    """
    try:
        await service.register(
            email=payload.email,
            password=payload.password,
        )
    except ValueError as e:
        if str(e) == "USER_ALREADY_EXISTS":
            raise HTTPException(
                status_code=409,
                detail="User already exists",
            )
        raise

    return UserCreateResponse()
