"""
In-memory repository implementations for CRM domain.

These are simple in-memory implementations for development/testing.
"""

from serp_crm.domain.entities import Contact, Lead, Opportunity, Partner
from serp_crm.domain.repositories import (
    IContactRepository,
    ILeadRepository,
    IOpportunityRepository,
    IPartnerRepository,
)


class InMemoryPartnerRepository(IPartnerRepository):
    """In-memory implementation of Partner repository."""

    def __init__(self) -> None:
        self._partners: dict[str, Partner] = {}

    async def get_by_id(self, partner_id: str) -> Partner | None:
        """Get partner by ID."""
        return self._partners.get(partner_id)

    async def get_by_email(self, email: str) -> Partner | None:
        """Get partner by email."""
        for partner in self._partners.values():
            if partner.email and str(partner.email) == email:
                return partner
        return None

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_customer: bool | None = None,
        is_supplier: bool | None = None,
        is_active: bool | None = None,
    ) -> list[Partner]:
        """List partners with optional filters."""
        partners = list(self._partners.values())

        if is_customer is not None:
            partners = [p for p in partners if p.is_customer == is_customer]
        if is_supplier is not None:
            partners = [p for p in partners if p.is_supplier == is_supplier]
        if is_active is not None:
            partners = [p for p in partners if p.is_active == is_active]

        return partners[skip : skip + limit]

    async def search(self, query: str) -> list[Partner]:
        """Search partners by name, email, or other fields."""
        query_lower = query.lower()
        results = []

        for partner in self._partners.values():
            if (
                query_lower in partner.name.lower()
                or (partner.email and query_lower in str(partner.email).lower())
                or (partner.website and query_lower in partner.website.lower())
            ):
                results.append(partner)

        return results

    async def save(self, partner: Partner) -> Partner:
        """Save (create or update) partner."""
        self._partners[partner.id] = partner
        return partner

    async def delete(self, partner_id: str) -> bool:
        """Delete partner."""
        if partner_id in self._partners:
            del self._partners[partner_id]
            return True
        return False

    async def count(
        self,
        is_customer: bool | None = None,
        is_supplier: bool | None = None,
        is_active: bool | None = None,
    ) -> int:
        """Count partners with optional filters."""
        partners = list(self._partners.values())

        if is_customer is not None:
            partners = [p for p in partners if p.is_customer == is_customer]
        if is_supplier is not None:
            partners = [p for p in partners if p.is_supplier == is_supplier]
        if is_active is not None:
            partners = [p for p in partners if p.is_active == is_active]

        return len(partners)


class InMemoryContactRepository(IContactRepository):
    """In-memory implementation of Contact repository."""

    def __init__(self) -> None:
        self._contacts: dict[str, Contact] = {}

    async def get_by_id(self, contact_id: str) -> Contact | None:
        """Get contact by ID."""
        return self._contacts.get(contact_id)

    async def get_by_partner_id(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Contact]:
        """Get contacts for a specific partner."""
        contacts = [c for c in self._contacts.values() if c.partner_id == partner_id]
        return contacts[skip : skip + limit]

    async def get_primary_contact(self, partner_id: str) -> Contact | None:
        """Get primary contact for a partner."""
        for contact in self._contacts.values():
            if contact.partner_id == partner_id and contact.is_primary:
                return contact
        return None

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> list[Contact]:
        """List contacts with optional filters."""
        contacts = list(self._contacts.values())

        if is_active is not None:
            contacts = [c for c in contacts if c.is_active == is_active]

        return contacts[skip : skip + limit]

    async def save(self, contact: Contact) -> Contact:
        """Save (create or update) contact."""
        self._contacts[contact.id] = contact
        return contact

    async def delete(self, contact_id: str) -> bool:
        """Delete contact."""
        if contact_id in self._contacts:
            del self._contacts[contact_id]
            return True
        return False

    async def count(self, partner_id: str | None = None) -> int:
        """Count contacts, optionally for a specific partner."""
        if partner_id:
            return len(
                [c for c in self._contacts.values() if c.partner_id == partner_id]
            )
        return len(self._contacts)


class InMemoryLeadRepository(ILeadRepository):
    """In-memory implementation of Lead repository."""

    def __init__(self) -> None:
        self._leads: dict[str, Lead] = {}

    async def get_by_id(self, lead_id: str) -> Lead | None:
        """Get lead by ID."""
        return self._leads.get(lead_id)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[Lead]:
        """List leads with optional filters."""
        leads = list(self._leads.values())

        if status is not None:
            leads = [lead for lead in leads if lead.status.value == status]

        return leads[skip : skip + limit]

    async def search(self, query: str) -> list[Lead]:
        """Search leads by name, company, email, or other fields."""
        query_lower = query.lower()
        results = []

        for lead in self._leads.values():
            if (
                query_lower in lead.name.lower()
                or (lead.company and query_lower in lead.company.lower())
                or (lead.email and query_lower in str(lead.email).lower())
            ):
                results.append(lead)

        return results

    async def save(self, lead: Lead) -> Lead:
        """Save (create or update) lead."""
        self._leads[lead.id] = lead
        return lead

    async def delete(self, lead_id: str) -> bool:
        """Delete lead."""
        if lead_id in self._leads:
            del self._leads[lead_id]
            return True
        return False

    async def count(self, status: str | None = None) -> int:
        """Count leads with optional filters."""
        if status is not None:
            return len(
                [lead for lead in self._leads.values() if lead.status.value == status]
            )
        return len(self._leads)


class InMemoryOpportunityRepository(IOpportunityRepository):
    """In-memory implementation of Opportunity repository."""

    def __init__(self) -> None:
        self._opportunities: dict[str, Opportunity] = {}

    async def get_by_id(self, opportunity_id: str) -> Opportunity | None:
        """Get opportunity by ID."""
        return self._opportunities.get(opportunity_id)

    async def get_by_partner_id(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Opportunity]:
        """Get opportunities for a specific partner."""
        opportunities = [
            o for o in self._opportunities.values() if o.partner_id == partner_id
        ]
        return opportunities[skip : skip + limit]

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        stage: str | None = None,
    ) -> list[Opportunity]:
        """List opportunities with optional filters."""
        opportunities = list(self._opportunities.values())

        if stage is not None:
            opportunities = [o for o in opportunities if o.stage.value == stage]

        return opportunities[skip : skip + limit]

    async def save(self, opportunity: Opportunity) -> Opportunity:
        """Save (create or update) opportunity."""
        self._opportunities[opportunity.id] = opportunity
        return opportunity

    async def delete(self, opportunity_id: str) -> bool:
        """Delete opportunity."""
        if opportunity_id in self._opportunities:
            del self._opportunities[opportunity_id]
            return True
        return False

    async def count(
        self, partner_id: str | None = None, stage: str | None = None
    ) -> int:
        """Count opportunities with optional filters."""
        opportunities = list(self._opportunities.values())

        if partner_id is not None:
            opportunities = [o for o in opportunities if o.partner_id == partner_id]
        if stage is not None:
            opportunities = [o for o in opportunities if o.stage.value == stage]

        return len(opportunities)
