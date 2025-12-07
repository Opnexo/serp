"""
Configuration for serp-common module.
"""

from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    """Common module settings."""

    # Module metadata
    module_name: str = "Common"
    module_version: str = "0.1.0"

    # Database configuration with schema isolation
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/serp"
    database_schema: str = "common"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Feature flags
    enable_address_validation: bool = True

    # Business rules
    default_country: str = "US"

    class Config:
        env_prefix = "SERP_COMMON_"
        case_sensitive = False


_settings: CommonSettings | None = None


def get_settings() -> CommonSettings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = CommonSettings()
    return _settings
