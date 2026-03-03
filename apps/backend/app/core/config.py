"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "NanaHouse API"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://root:root@localhost:5432/nanahouse"

    model_config = {"env_prefix": "NANA_", "env_file": ".env"}


settings = Settings()
