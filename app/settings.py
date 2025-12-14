from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta
from pydantic import Field


class AppSettings(BaseSettings):
    # Application
    app_name: str = "user-registration-api"
    description: str = "simple user registration api"
    version: str = "0.1.0"

    # MySQL Database
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str

    # Pool settings
    db_pool_min_size: int = Field(default=5)
    db_pool_max_size: int = Field(default=20)

    # activation code tll
    activation_code_ttl = timedelta(minutes=1)

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        return (
            f"mysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


settings = AppSettings()
