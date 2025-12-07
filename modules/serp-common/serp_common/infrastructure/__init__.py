"""
Infrastructure layer for serp-common module.
"""

# Database management
from serp_common.infrastructure.persistence.database import (
    DatabaseManager,
    get_database_manager,
    get_session,
)

# SQLAlchemy models
from serp_common.infrastructure.persistence.models import (
    Base,
    AddressModel,
)

# Repository implementations
from serp_common.infrastructure.persistence.repositories import (
    # In-memory (testing)
    InMemoryAddressRepository,
    # PostgreSQL (production)
    PostgresAddressRepository,
    # Backward compatibility aliases
    SQLAlchemyAddressRepository,
)

__all__ = [
    # Repositories
    "InMemoryAddressRepository",
    "PostgresAddressRepository",
    "SQLAlchemyAddressRepository",
    # Database
    "DatabaseManager",
    "get_database_manager",
    "get_session",
    # Models
    "Base",
    "AddressModel",
]
