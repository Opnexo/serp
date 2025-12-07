"""
Base ValueObject class for Domain-Driven Design
"""

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject(ABC):
    """
    Base class for domain value objects.

    Value Objects have:
    - No unique identity
    - Immutable state (frozen dataclass)
    - Equality based on all attributes
    - Validation in __post_init__

    Example:
        @dataclass(frozen=True)
        class Email(ValueObject):
            address: str

            def __post_init__(self):
                if '@' not in self.address:
                    raise ValueError("Invalid email address")

        @dataclass(frozen=True)
        class Money(ValueObject):
            amount: Decimal
            currency: str

            def __post_init__(self):
                if self.amount < 0:
                    raise ValueError("Amount cannot be negative")
    """

    pass
