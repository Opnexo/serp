"""
Standard exceptions for SERP
"""

from serp_core.exceptions.application import (
    ApplicationError,
    ValidationError,
)
from serp_core.exceptions.auth import (
    AuthenticationError,
    PermissionDeniedError,
)
from serp_core.exceptions.domain import (
    DomainError,
    EntityNotFoundError,
    InvalidOperationError,
)
from serp_core.exceptions.events import (
    EventError,
    EventPublishError,
    EventDeserializationError,
    EventHandlerError,
    EventBusConnectionError,
    UnknownEventTypeError,
    EventSubscriptionError,
)

__all__ = [
    # Domain
    "DomainError",
    "EntityNotFoundError",
    "InvalidOperationError",
    # Application
    "ApplicationError",
    "ValidationError",
    # Auth
    "AuthenticationError",
    "PermissionDeniedError",
    # Events
    "EventError",
    "EventPublishError",
    "EventDeserializationError",
    "EventHandlerError",
    "EventBusConnectionError",
    "UnknownEventTypeError",
    "EventSubscriptionError",
]

