"""Infrastructure layer for CRM module."""

# Database management
from serp_crm.infrastructure.persistence.database import (
    DatabaseManager,
    get_database_manager,
    get_session,
)

# SQLAlchemy models
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
    # In-memory (for testing)
    InMemoryContactRepository,
    InMemoryLeadRepository,
    InMemoryOpportunityRepository,
    InMemoryPartnerRepository,
    # PostgreSQL (for production)
    PostgresContactRepository,
    PostgresLeadRepository,
    PostgresOpportunityRepository,
    PostgresPartnerRepository,
    # Backward compatibility aliases
    SQLAlchemyContactRepository,
    SQLAlchemyLeadRepository,
    SQLAlchemyOpportunityRepository,
    SQLAlchemyPartnerRepository,
)

__all__ = [
    # In-memory repositories (for testing)
    "InMemoryContactRepository",
    "InMemoryLeadRepository",
    "InMemoryOpportunityRepository",
    "InMemoryPartnerRepository",
    # PostgreSQL repositories (for production)
    "PostgresContactRepository",
    "PostgresLeadRepository",
    "PostgresOpportunityRepository",
    "PostgresPartnerRepository",
    # Backward compatibility aliases
    "SQLAlchemyContactRepository",
    "SQLAlchemyLeadRepository",
    "SQLAlchemyOpportunityRepository",
    "SQLAlchemyPartnerRepository",
    # Database management
    "DatabaseManager",
    "get_database_manager",
    "get_session",
    # SQLAlchemy models
    "Base",
    "PartnerModel",
    "ContactModel",
    "LeadModel",
    "OpportunityModel",
    "ActivityModel",
]
