"""Email value object."""

import re
from dataclasses import dataclass

from serp_core.domain.value_object import ValueObject


@dataclass(frozen=True)
class Email(ValueObject):
    """
    Email address value object.

    Validates email format and provides immutable storage.
    """

    value: str

    # Basic email regex pattern
    _EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Email address cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Email address too long (max 255 characters)")
        if not self._EMAIL_PATTERN.match(self.value):
            raise ValueError(f"Invalid email address format: {self.value}")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Email):
            return self.value.lower() == other.value.lower()
        if isinstance(other, str):
            return self.value.lower() == other.lower()
        return False

    def __hash__(self) -> int:
        return hash(self.value.lower())

    @property
    def local_part(self) -> str:
        """Get the local part (before @) of the email."""
        return self.value.split("@")[0]

    @property
    def domain(self) -> str:
        """Get the domain part (after @) of the email."""
        return self.value.split("@")[1]
