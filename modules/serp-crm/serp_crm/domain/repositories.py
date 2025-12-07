"""
Repository interfaces for CRM domain.
"""

from abc import ABC, abstractmethod

from serp_crm.domain.entities import Contact, Lead, Opportunity, Partner


class IPartnerRepository(ABC):
    """Repository interface for Partner aggregate."""

    @abstractmethod
    async def get_by_id(self, partner_id: str) -> Partner | None:
        """Get partner by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Partner | None:
        """Get partner by email."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_customer: bool | None = None,
        is_supplier: bool | None = None,
        is_active: bool | None = None,
    ) -> list[Partner]:
        """List partners with optional filters."""
        pass

    @abstractmethod
    async def search(self, query: str) -> list[Partner]:
        """Search partners by name, email, or other fields."""
        pass

    @abstractmethod
    async def save(self, partner: Partner) -> Partner:
        """Save (create or update) partner."""
        pass

    @abstractmethod
    async def delete(self, partner_id: str) -> bool:
        """Delete partner."""
        pass

    @abstractmethod
    async def count(
        self,
        is_customer: bool | None = None,
        is_supplier: bool | None = None,
        is_active: bool | None = None,
    ) -> int:
        """Count partners with optional filters."""
        pass


class IContactRepository(ABC):
    """Repository interface for Contact aggregate."""

    @abstractmethod
    async def get_by_id(self, contact_id: str) -> Contact | None:
        """Get contact by ID."""
        pass

    @abstractmethod
    async def get_by_partner_id(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Contact]:
        """Get contacts for a specific partner."""
        pass

    @abstractmethod
    async def get_primary_contact(self, partner_id: str) -> Contact | None:
        """Get primary contact for a partner."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> list[Contact]:
        """List contacts with optional filters."""
        pass

    @abstractmethod
    async def save(self, contact: Contact) -> Contact:
        """Save (create or update) contact."""
        pass

    @abstractmethod
    async def delete(self, contact_id: str) -> bool:
        """Delete contact."""
        pass

    @abstractmethod
    async def count(self, partner_id: str | None = None) -> int:
        """Count contacts, optionally for a specific partner."""
        pass


class ILeadRepository(ABC):
    """Repository interface for Lead aggregate."""

    @abstractmethod
    async def get_by_id(self, lead_id: str) -> Lead | None:
        """Get lead by ID."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[Lead]:
        """List leads with optional filters."""
        pass

    @abstractmethod
    async def search(self, query: str) -> list[Lead]:
        """Search leads by name, company, email, or other fields."""
        pass

    @abstractmethod
    async def save(self, lead: Lead) -> Lead:
        """Save (create or update) lead."""
        pass

    @abstractmethod
    async def delete(self, lead_id: str) -> bool:
        """Delete lead."""
        pass

    @abstractmethod
    async def count(self, status: str | None = None) -> int:
        """Count leads with optional filters."""
        pass


class IOpportunityRepository(ABC):
    """Repository interface for Opportunity aggregate."""

    @abstractmethod
    async def get_by_id(self, opportunity_id: str) -> Opportunity | None:
        """Get opportunity by ID."""
        pass

    @abstractmethod
    async def get_by_partner_id(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Opportunity]:
        """Get opportunities for a specific partner."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        stage: str | None = None,
    ) -> list[Opportunity]:
        """List opportunities with optional filters."""
        pass

    @abstractmethod
    async def save(self, opportunity: Opportunity) -> Opportunity:
        """Save (create or update) opportunity."""
        pass

    @abstractmethod
    async def delete(self, opportunity_id: str) -> bool:
        """Delete opportunity."""
        pass

    @abstractmethod
    async def count(
        self, partner_id: str | None = None, stage: str | None = None
    ) -> int:
        """Count opportunities with optional filters."""
        pass
