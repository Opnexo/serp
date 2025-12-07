"""
Domain layer base classes for DDD patterns
"""

from serp_core.domain.aggregate import AggregateRoot
from serp_core.domain.entity import Entity
from serp_core.domain.events import DomainEvent, DomainEventHandler
from serp_core.domain.repository import Repository
from serp_core.domain.service import DomainService
from serp_core.domain.value_object import ValueObject

__all__ = [
    "Entity",
    "ValueObject",
    "AggregateRoot",
    "Repository",
    "DomainService",
    "DomainEvent",
    "DomainEventHandler",
]
