from fastapi import FastAPI
from app.api.router.healthcheck import router as healthcheck_router
from app.api.router.users import router as user_router
from app.api.router.activation import router as activation_router

def create_app() -> FastAPI:
    app = FastAPI(title="User Registration API", version="0.1.0")

    routers = healthcheck_router, user_router, activation_router
    for router in routers:
        app.include_router(router)

    return app

app = create_app()