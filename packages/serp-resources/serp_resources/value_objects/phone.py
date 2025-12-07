"""Phone number value object."""

import re
from dataclasses import dataclass

from serp_core.domain.value_object import ValueObject


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    """
    Phone number value object.

    Stores phone numbers in a normalized format (digits and + only).
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Phone number cannot be empty")

        # Remove common formatting characters, keep digits and +
        cleaned = re.sub(r"[^\d+]", "", self.value)

        if len(cleaned) < 7:
            raise ValueError(f"Phone number too short: {self.value}")
        if len(cleaned) > 20:
            raise ValueError(f"Phone number too long: {self.value}")

        # Store the cleaned value
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PhoneNumber):
            return self.value == other.value
        if isinstance(other, str):
            cleaned = re.sub(r"[^\d+]", "", other)
            return self.value == cleaned
        return False

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def formatted(self) -> str:
        """
        Get a formatted version of the phone number.

        Basic formatting - can be extended for international formats.
        """
        if self.value.startswith("+"):
            # International format
            return self.value
        elif len(self.value) == 10:
            # US format: (XXX) XXX-XXXX
            return f"({self.value[:3]}) {self.value[3:6]}-{self.value[6:]}"
        else:
            return self.value

    @property
    def country_code(self) -> str | None:
        """Get the country code if present (starts with +)."""
        if self.value.startswith("+"):
            # Simple extraction - first 1-3 digits after +
            match = re.match(r"\+(\d{1,3})", self.value)
            if match:
                return match.group(1)
        return None
