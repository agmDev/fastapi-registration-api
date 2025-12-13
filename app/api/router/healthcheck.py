from fastapi import APIRouter

from app.api.models.health import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["healthcech"]
)

@router.get(
    "",
    response_model=HealthResponse
)
async def healthcheck() -> HealthResponse:
    return HealthResponse()