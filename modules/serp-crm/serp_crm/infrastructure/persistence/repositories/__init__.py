"""
Repository implementations for CRM module.

This package contains all repository implementations:
- memory.py: In-memory implementations for testing
- postgres.py: PostgreSQL/SQLAlchemy implementations for production
"""

# In-memory repositories (for testing)
from serp_crm.infrastructure.persistence.repositories.memory import (
    InMemoryContactRepository,
    InMemoryLeadRepository,
    InMemoryOpportunityRepository,
    InMemoryPartnerRepository,
)

# PostgreSQL repositories (for production)
from serp_crm.infrastructure.persistence.repositories.postgres import (
    PostgresContactRepository,
    PostgresLeadRepository,
    PostgresOpportunityRepository,
    PostgresPartnerRepository,
)

# Backward compatibility aliases
SQLAlchemyPartnerRepository = PostgresPartnerRepository
SQLAlchemyContactRepository = PostgresContactRepository
SQLAlchemyLeadRepository = PostgresLeadRepository
SQLAlchemyOpportunityRepository = PostgresOpportunityRepository

__all__ = [
    # In-memory (testing)
    "InMemoryContactRepository",
    "InMemoryLeadRepository",
    "InMemoryOpportunityRepository",
    "InMemoryPartnerRepository",
    # PostgreSQL (production)
    "PostgresContactRepository",
    "PostgresLeadRepository",
    "PostgresOpportunityRepository",
    "PostgresPartnerRepository",
    # Backward compatibility aliases
    "SQLAlchemyPartnerRepository",
    "SQLAlchemyContactRepository",
    "SQLAlchemyLeadRepository",
    "SQLAlchemyOpportunityRepository",
]
