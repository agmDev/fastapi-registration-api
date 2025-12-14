from fastapi import APIRouter, Depends

from app.services.users_service import UsersService
from app.api.dependencies.auth import get_current_user_id
from app.api.dependencies.services import get_users_service
from app.api.models.activation import (
    ActivateAccountRequest,
    ActivateAccountResponse,
)

router = APIRouter(
    prefix="/activation",
    tags=["activation"],
)


@router.post(
    "",
    response_model=ActivateAccountResponse,
)
async def activate_account(
    payload: ActivateAccountRequest,
    user_id: int = Depends(get_current_user_id),
    service: UsersService = Depends(get_users_service)
) -> ActivateAccountResponse:
    """
    Activate a user account using a 4-digit code.
    Basic Auth is used to identify the user.
    """
    await service.activate(user_id, payload.code)

    return ActivateAccountResponse()
