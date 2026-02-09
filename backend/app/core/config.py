from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "ERPCenter"
    environment: str = "development"
    api_v1_prefix: str = "/v1"
    secret_key: str = Field(..., min_length=32)
    access_token_exp_minutes: int = 15
    refresh_token_exp_days: int = 7
    algorithm: str = "HS256"
    database_url: str
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    log_level: str = "INFO"
    enable_metrics: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
