"""
Persistence layer for CRM module.

Contains SQLAlchemy models, database configuration, repositories, and migrations.
"""

from serp_crm.infrastructure.persistence.models import (
    ActivityModel,
    Base,
    ContactModel,
    LeadModel,
    OpportunityModel,
    PartnerModel,
)

# Repository implementations
from serp_crm.infrastructure.persistence.repositories import (
    InMemoryContactRepository,
    InMemoryLeadRepository,
    InMemoryOpportunityRepository,
    InMemoryPartnerRepository,
    PostgresContactRepository,
    PostgresLeadRepository,
    PostgresOpportunityRepository,
    PostgresPartnerRepository,
    SQLAlchemyContactRepository,
    SQLAlchemyLeadRepository,
    SQLAlchemyOpportunityRepository,
    SQLAlchemyPartnerRepository,
)

__all__ = [
    # SQLAlchemy models
    "Base",
    "PartnerModel",
    "ContactModel",
    "LeadModel",
    "OpportunityModel",
    "ActivityModel",
    # In-memory repositories (for testing)
    "InMemoryPartnerRepository",
    "InMemoryContactRepository",
    "InMemoryLeadRepository",
    "InMemoryOpportunityRepository",
    # PostgreSQL repositories (for production)
    "PostgresPartnerRepository",
    "PostgresContactRepository",
    "PostgresLeadRepository",
    "PostgresOpportunityRepository",
    # Backward compatibility aliases
    "SQLAlchemyPartnerRepository",
    "SQLAlchemyContactRepository",
    "SQLAlchemyLeadRepository",
    "SQLAlchemyOpportunityRepository",
]
