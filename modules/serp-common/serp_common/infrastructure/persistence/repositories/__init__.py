"""
Repository implementations for serp-common module.
"""

from serp_common.infrastructure.persistence.repositories.memory import (
    InMemoryAddressRepository,
)
from serp_common.infrastructure.persistence.repositories.postgres import (
    PostgresAddressRepository,
)

# Backward compatibility alias
SQLAlchemyAddressRepository = PostgresAddressRepository

__all__ = [
    "InMemoryAddressRepository",
    "PostgresAddressRepository",
    "SQLAlchemyAddressRepository",
]
