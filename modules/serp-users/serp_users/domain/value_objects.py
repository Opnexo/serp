"""Value objects for users module."""

import re
from dataclasses import dataclass

from serp_core.domain.value_object import ValueObject
from serp_core.exceptions.domain import ValidationError

# Re-export Email from serp-resources
from serp_resources import Email

__all__ = [
    "Email",
    "Password",
    "Username",
]


@dataclass(frozen=True)
class Password(ValueObject):
    """Password value object with validation."""

    value: str

    def __post_init__(self) -> None:
        """Validate password strength."""
        if not self.value:
            raise ValidationError("Password cannot be empty")

        if len(self.value) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        # Check for at least one uppercase, one lowercase, and one digit
        if not re.search(r"[A-Z]", self.value):
            raise ValidationError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", self.value):
            raise ValidationError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", self.value):
            raise ValidationError("Password must contain at least one digit")

    def __str__(self) -> str:
        return "********"  # Never expose the actual password

    def __repr__(self) -> str:
        return "Password(********)"


@dataclass(frozen=True)
class Username(ValueObject):
    """Username value object with validation."""

    value: str

    def __post_init__(self) -> None:
        """Validate username format."""
        if not self.value:
            raise ValidationError("Username cannot be empty")

        if len(self.value) < 3:
            raise ValidationError("Username must be at least 3 characters long")

        if len(self.value) > 50:
            raise ValidationError("Username must be at most 50 characters long")

        # Only alphanumeric, underscore, and hyphen allowed
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.value):
            raise ValidationError(
                "Username can only contain letters, numbers, underscore, and hyphen"
            )

    def __str__(self) -> str:
        return self.value
