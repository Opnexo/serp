"""
Configuration management for serp-shell
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from serp_core.config import Settings


class ShellSettings(Settings):
    """
    Settings for serp-shell application.

    Configuration can come from:
    - Environment variables (SERP_*)
    - .env file
    - config/settings.yaml (if using YAML loader)
    """

    # App settings
    app_title: str = Field(default="SimpleERP", env="SERP_APP_TITLE")
    app_version: str = Field(default="1.0.0", env="SERP_APP_VERSION")
    debug: bool = Field(default=False, env="SERP_DEBUG")

    # Server settings
    host: str = Field(default="0.0.0.0", env="SERP_HOST")
    port: int = Field(default=8000, env="SERP_PORT")
    reload: bool = Field(default=False, env="SERP_RELOAD")

    # CORS settings
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        env="SERP_CORS_ORIGINS",
    )

    # Module settings
    enabled_modules: List[str] = Field(
        default_factory=lambda: ["serp-users", "serp-common", "serp-crm"],
        env="SERP_ENABLED_MODULES",
    )
    enable_all_modules: bool = Field(default=True, env="SERP_ENABLE_ALL_MODULES")

    # Database settings
    database_url: str = Field(default="sqlite:///./serp.db", env="SERP_DATABASE_URL")

    # Auth settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production", env="SERP_SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="SERP_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="SERP_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    class Config:
        env_file = ".env"
        env_prefix = "SERP_"


@lru_cache()
def get_settings() -> ShellSettings:
    """Get cached settings instance"""
    return ShellSettings()
