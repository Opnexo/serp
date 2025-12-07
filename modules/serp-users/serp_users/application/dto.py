"""DTOs for users module."""

from datetime import datetime

from pydantic import Field, field_validator
from serp_core.application.dto import DTO


class UserDTO(DTO):
    """User data transfer object."""

    id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    tenant_id: str | None = None
    avatar_url: str | None = None
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserCreateDTO(DTO):
    """DTO for creating a user."""

    username: str = Field(min_length=3, max_length=50)
    email: str = Field(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=200)
    tenant_id: str | None = None
    is_active: bool = True
    is_superuser: bool = False

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdateDTO(DTO):
    """DTO for updating a user."""

    email: str | None = Field(
        None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    full_name: str | None = Field(None, min_length=1, max_length=200)
    avatar_url: str | None = None
    is_active: bool | None = None


class PasswordChangeDTO(DTO):
    """DTO for changing password."""

    current_password: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginDTO(DTO):
    """DTO for user login."""

    username: str
    password: str


class TokenDTO(DTO):
    """DTO for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RoleDTO(DTO):
    """Role data transfer object."""

    id: str
    name: str
    description: str
    permissions: list[str] = Field(default_factory=list)
    is_system: bool
    created_at: datetime
    updated_at: datetime


class RoleCreateDTO(DTO):
    """DTO for creating a role."""

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500)
    permissions: list[str] = Field(default_factory=list)


class RoleUpdateDTO(DTO):
    """DTO for updating a role."""

    description: str | None = Field(None, max_length=500)
    permissions: list[str] | None = None


class UserListDTO(DTO):
    """DTO for paginated user list."""

    items: list[UserDTO]
    total: int
    page: int
    page_size: int
    total_pages: int
