"""
Persistence layer for serp-common module.
"""

from serp_common.infrastructure.persistence.database import (
    DatabaseManager,
    get_database_manager,
    get_session,
)
from serp_common.infrastructure.persistence.models import Base, AddressModel
from serp_common.infrastructure.persistence.repositories import (
    InMemoryAddressRepository,
    PostgresAddressRepository,
    SQLAlchemyAddressRepository,
)

__all__ = [
    "DatabaseManager",
    "get_database_manager",
    "get_session",
    "Base",
    "AddressModel",
    "InMemoryAddressRepository",
    "PostgresAddressRepository",
    "SQLAlchemyAddressRepository",
]
