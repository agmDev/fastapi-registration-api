from fastapi import FastAPI
from app.api.healthcheck import router as healthcheck_router

def create_app() -> FastAPI:
    app = FastAPI(title="User Registration API", version="0.1.0")

    # Include routes
    app.include_router(healthcheck_router)

    return app

app = create_app()