from fastapi import Request
from app.infrastructure.database import Database


def get_db(request: Request) -> Database:
    return request.app.state.db
