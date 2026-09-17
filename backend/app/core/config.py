"""Application configuration."""

from dataclasses import dataclass
from typing import List
from pathlib import Path

from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    """Static settings used while the application configuration grows."""
    model_config = SettingsConfigDict(
        env_file="env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = Field(..., description="Application name")
    # API_V1_STR: str = Field(..., description="API version string")
    ALLOWED_ORIGINS: List[str] = Field(..., description="List of allowed origins")
    DATABASE_URL: str = Field(..., description="Database URL")
    BASE_DIR: Path = Field(default= Path.cwd().parent.parent.parent)
    PROJECT_NAME : str = "Monoflight API"
    API_V1_PREFIX: str = "/api/v1"

    FRONT_DIR = BASE_DIR / "frontend"
    STATIC_DIR = FRONT_DIR / "static"
    TEMPLATES_DIR = FRONT_DIR / "templates"


    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | List[str]) -> List[str]:
        """Parse allowed origins from a string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v or ["*"]



settings = Settings()  # type: ignore[call-arg]  # Values are loaded from environment settings.
