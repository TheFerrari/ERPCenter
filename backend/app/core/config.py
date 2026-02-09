from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    app_name: str = "ERPCenter API"
    environment: str = "development"
    database_url: str = Field(
        "postgresql+asyncpg://erp:erp@postgres:5432/erpcenter",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field("change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7
    cors_allow_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"


settings = Settings()
