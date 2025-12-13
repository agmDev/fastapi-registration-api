from fastapi import APIRouter, status
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
    payload: UserCreateRequest
) -> UserCreateResponse:
    """
    Create a new user and send an activation code by email.
    """
    return UserCreateResponse()