from pydantic_settings import BaseSettings
from functools import lru_cache


class AppSettings(BaseSettings):
    app_name: str = "user-registration-api"
    version: str = "0.1.0"


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()