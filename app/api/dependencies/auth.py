from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.api.dependencies.services import get_users_service
from app.services.users_service import UsersService


security = HTTPBasic()


async def get_current_user_id(
    credentials: HTTPBasicCredentials = Depends(security),
    service: UsersService = Depends(get_users_service),
) -> int:
    user_id = await service.verify_credentials(
        credentials.username,
        credentials.password,
    )
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user_id
