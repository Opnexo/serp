"""Money value object."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from serp_core.domain.value_object import ValueObject


@dataclass(frozen=True)
class Money(ValueObject):
    """
    Money value object with currency.

    Represents a monetary amount with a specific currency.
    Supports arithmetic operations between same-currency amounts.
    """

    amount: Decimal
    currency: str  # ISO 4217 code (USD, EUR, GBP, etc.)

    def __post_init__(self) -> None:
        # Convert to Decimal if needed
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

        # Validate currency code (ISO 4217 is 3 uppercase letters)
        if not self.currency or len(self.currency) != 3:
            raise ValueError(f"Invalid currency code: {self.currency}")
        if not self.currency.isalpha():
            raise ValueError(f"Currency code must be letters: {self.currency}")

        # Normalize currency to uppercase
        object.__setattr__(self, "currency", self.currency.upper())

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError(f"Cannot add Money and {type(other).__name__}")
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError(f"Cannot subtract Money and {type(other).__name__}")
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | float | Decimal) -> "Money":
        if isinstance(factor, (int, float)):
            factor = Decimal(str(factor))
        return Money(self.amount * factor, self.currency)

    def __rmul__(self, factor: int | float | Decimal) -> "Money":
        return self.__mul__(factor)

    def __truediv__(self, divisor: int | float | Decimal) -> "Money":
        if isinstance(divisor, (int, float)):
            divisor = Decimal(str(divisor))
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / divisor, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __abs__(self) -> "Money":
        return Money(abs(self.amount), self.currency)

    def __lt__(self, other: "Money") -> bool:
        self._ensure_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._ensure_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._ensure_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        self._ensure_same_currency(other)
        return self.amount >= other.amount

    def _ensure_same_currency(self, other: "Money") -> None:
        if not isinstance(other, Money):
            raise TypeError(f"Cannot compare Money and {type(other).__name__}")
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )

    def round(self, decimal_places: int = 2) -> "Money":
        """Round to specified decimal places."""
        quantize_str = "0." + "0" * decimal_places
        rounded = self.amount.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
        return Money(rounded, self.currency)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "amount": str(self.amount),
            "currency": self.currency,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Money":
        """Create Money from dictionary."""
        return cls(
            amount=Decimal(data["amount"]),
            currency=data["currency"],
        )

    @classmethod
    def zero(cls, currency: str) -> "Money":
        """Create a zero amount in the specified currency."""
        return cls(Decimal("0"), currency)

    @property
    def is_zero(self) -> bool:
        """Check if the amount is zero."""
        return self.amount == 0

    @property
    def is_positive(self) -> bool:
        """Check if the amount is positive."""
        return self.amount > 0

    @property
    def is_negative(self) -> bool:
        """Check if the amount is negative."""
        return self.amount < 0
