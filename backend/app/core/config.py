"""Application configuration."""c

from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Static settings - loaded from environment variables only."""

    # Don't look for .env file, just use env vars
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
        env_file=".env"
    )

    APP_NAME: str
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode]
    DATABASE_URL: str
    PROJECT_NAME: str = "Monoflight API"
    API_V1_PREFIX: str = "/api/v1"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list[str]) -> list[str]:
        """Parse allowed origins from a string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v or ["*"]


settings = Settings()  # type: ignore[call-arg]  # Values are loaded from environment settings.
