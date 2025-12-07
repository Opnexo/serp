"""Tax ID value object."""

from dataclasses import dataclass
from typing import Any

from serp_core.domain.value_object import ValueObject


@dataclass(frozen=True)
class TaxId(ValueObject):
    """
    Tax identification number value object.

    Represents a tax ID with country code.
    Examples: VAT number (EU), EIN (US), CNPJ (Brazil), etc.
    """

    value: str
    country: str  # ISO 3166-1 alpha-2 code (US, GB, DE, BR, etc.)

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Tax ID value cannot be empty")

        # Validate country code (ISO 3166-1 alpha-2 is 2 uppercase letters)
        if not self.country or len(self.country) != 2:
            raise ValueError(f"Invalid country code: {self.country}")
        if not self.country.isalpha():
            raise ValueError(f"Country code must be letters: {self.country}")

        # Normalize: strip whitespace from value, uppercase country
        object.__setattr__(self, "value", self.value.strip())
        object.__setattr__(self, "country", self.country.upper())

    def __str__(self) -> str:
        return f"{self.country}-{self.value}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TaxId):
            return self.value == other.value and self.country == other.country
        return False

    def __hash__(self) -> int:
        return hash((self.value, self.country))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "value": self.value,
            "country": self.country,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaxId":
        """Create TaxId from dictionary."""
        return cls(
            value=data["value"],
            country=data["country"],
        )

    @property
    def formatted(self) -> str:
        """Get formatted tax ID with country prefix."""
        return f"{self.country}-{self.value}"

    @property
    def raw_value(self) -> str:
        """Get raw tax ID value without country prefix."""
        return self.value
