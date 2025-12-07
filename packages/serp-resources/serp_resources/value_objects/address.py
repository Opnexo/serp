"""Address value object."""

from dataclasses import dataclass
from typing import Any

from serp_core.domain.value_object import ValueObject


@dataclass(frozen=True)
class Address(ValueObject):
    """
    Physical address value object.

    Represents a complete postal address with validation.
    """

    street: str
    city: str
    country: str
    state: str | None = None
    postal_code: str | None = None

    def __post_init__(self) -> None:
        if not self.street or not self.street.strip():
            raise ValueError("Street address is required")
        if not self.city or not self.city.strip():
            raise ValueError("City is required")
        if not self.country or not self.country.strip():
            raise ValueError("Country is required")

    def __str__(self) -> str:
        parts = [self.street, self.city]
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        parts.append(self.country)
        return ", ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Address":
        """Create Address from dictionary."""
        return cls(
            street=data["street"],
            city=data["city"],
            country=data["country"],
            state=data.get("state"),
            postal_code=data.get("postal_code"),
        )

    @property
    def single_line(self) -> str:
        """Get address as a single line."""
        return str(self)

    @property
    def multi_line(self) -> str:
        """Get address as multiple lines."""
        lines = [self.street, self.city]
        if self.state and self.postal_code:
            lines.append(f"{self.state} {self.postal_code}")
        elif self.state:
            lines.append(self.state)
        elif self.postal_code:
            lines.append(self.postal_code)
        lines.append(self.country)
        return "\n".join(lines)
