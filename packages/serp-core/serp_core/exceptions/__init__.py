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

__all__ = [
    "DomainError",
    "EntityNotFoundError",
    "InvalidOperationError",
    "ApplicationError",
    "ValidationError",
    "AuthenticationError",
    "PermissionDeniedError",
]
