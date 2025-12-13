from pydantic_settings import BaseSettings
from functools import lru_cache


class AppSettings(BaseSettings):
    app_name: str = "user-registration-api"


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()