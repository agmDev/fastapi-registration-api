from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

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
) -> ActivateAccountResponse:
    """
    Activate a user account using a 4-digit code.
    Basic Auth is used to identify the user.
    """
    return ActivateAccountResponse()