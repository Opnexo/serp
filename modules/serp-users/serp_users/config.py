"""Configuration for users module."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class UsersSettings(BaseSettings):
    """Settings for users module."""

    model_config = SettingsConfigDict(
        env_prefix="SERP_USERS_",
        env_file=".env",
        case_sensitive=False,
    )

    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Password Policy
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = False

    # User defaults
    default_user_is_active: bool = True
    allow_user_registration: bool = True
