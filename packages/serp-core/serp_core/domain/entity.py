"""
Base Entity class for Domain-Driven Design
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class Entity(ABC):
    """
    Base class for domain entities.

    Entities have:
    - Unique identity (id)
    - Mutable state
    - Business logic methods
    - Lifecycle (created_at, updated_at)

    Example:
        @dataclass
        class Customer(Entity):
            name: str
            email: str

            def change_email(self, new_email: str) -> None:
                self.email = new_email
                self._mark_updated()
    """

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def _mark_updated(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()

    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they have the same id and type"""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id and type(self) == type(other)

    def __hash__(self) -> int:
        """Hash based on id"""
        return hash(self.id)
