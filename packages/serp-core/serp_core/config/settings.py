"""
Base Settings class for configuration management
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Base class for application settings.

    Uses Pydantic for validation and environment variable loading.

    Example:
        class AppSettings(Settings):
            database_url: str
            secret_key: str
            debug: bool = False

            class Config:
                env_file = ".env"
                env_prefix = "SERP_"

        # Usage
        settings = AppSettings()
        print(settings.database_url)  # From SERP_DATABASE_URL env var
    """

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
