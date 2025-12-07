"""
PostgreSQL/SQLAlchemy repository implementations for CRM domain.
"""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from serp_crm.domain.entities import Contact, Lead, Opportunity, Partner
from serp_crm.domain.repositories import (
    IContactRepository,
    ILeadRepository,
    IOpportunityRepository,
    IPartnerRepository,
)
from serp_crm.infrastructure.persistence.mappers import (
    ContactMapper,
    LeadMapper,
    OpportunityMapper,
    PartnerMapper,
)
from serp_crm.infrastructure.persistence.models import (
    ContactModel,
    LeadModel,
    OpportunityModel,
    PartnerModel,
)


class PostgresPartnerRepository(IPartnerRepository):
    """PostgreSQL implementation of Partner repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, partner_id: str) -> Partner | None:
        """Get partner by ID."""
        result = await self._session.execute(
            select(PartnerModel).where(PartnerModel.id == partner_id)
        )
        model = result.scalar_one_or_none()
        return PartnerMapper.to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Partner | None:
        """Get partner by email."""
        result = await self._session.execute(
            select(PartnerModel).where(PartnerModel.email == email)
        )
        model = result.scalar_one_or_none()
        return PartnerMapper.to_entity(model) if model else None

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_customer: bool | None = None,
        is_supplier: bool | None = None,
        is_active: bool | None = None,
    ) -> list[Partner]:
        """List partners with optional filters."""
        query = select(PartnerModel)

        if is_customer is not None:
            query = query.where(PartnerModel.is_customer == is_customer)
        if is_supplier is not None:
            query = query.where(PartnerModel.is_supplier == is_supplier)
        if is_active is not None:
            query = query.where(PartnerModel.is_active == is_active)

        query = query.order_by(PartnerModel.name).offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [PartnerMapper.to_entity(model) for model in models]

    async def search(self, query: str) -> list[Partner]:
        """Search partners by name, email, or other fields."""
        search_pattern = f"%{query}%"
        stmt = (
            select(PartnerModel)
            .where(
                or_(
                    PartnerModel.name.ilike(search_pattern),
                    PartnerModel.email.ilike(search_pattern),
                    PartnerModel.website.ilike(search_pattern),
                )
            )
            .order_by(PartnerModel.name)
            .limit(50)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [PartnerMapper.to_entity(model) for model in models]

    async def save(self, partner: Partner) -> Partner:
        """Save (create or update) partner."""
        result = await self._session.execute(
            select(PartnerModel).where(PartnerModel.id == partner.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            PartnerMapper.update_model(existing, partner)
            await self._session.flush()
            return PartnerMapper.to_entity(existing)
        else:
            model = PartnerMapper.to_model(partner)
            self._session.add(model)
            await self._session.flush()
            return PartnerMapper.to_entity(model)

    async def delete(self, partner_id: str) -> bool:
        """Delete partner."""
        result = await self._session.execute(
            select(PartnerModel).where(PartnerModel.id == partner_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def count(
        self,
        is_customer: bool | None = None,
        is_supplier: bool | None = None,
        is_active: bool | None = None,
    ) -> int:
        """Count partners with optional filters."""
        query = select(func.count(PartnerModel.id))

        if is_customer is not None:
            query = query.where(PartnerModel.is_customer == is_customer)
        if is_supplier is not None:
            query = query.where(PartnerModel.is_supplier == is_supplier)
        if is_active is not None:
            query = query.where(PartnerModel.is_active == is_active)

        result = await self._session.execute(query)
        return result.scalar() or 0


class PostgresContactRepository(IContactRepository):
    """PostgreSQL implementation of Contact repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, contact_id: str) -> Contact | None:
        """Get contact by ID."""
        result = await self._session.execute(
            select(ContactModel).where(ContactModel.id == contact_id)
        )
        model = result.scalar_one_or_none()
        return ContactMapper.to_entity(model) if model else None

    async def get_by_partner_id(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Contact]:
        """Get contacts for a specific partner."""
        query = (
            select(ContactModel)
            .where(ContactModel.partner_id == partner_id)
            .order_by(ContactModel.is_primary.desc(), ContactModel.last_name)
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [ContactMapper.to_entity(model) for model in models]

    async def get_primary_contact(self, partner_id: str) -> Contact | None:
        """Get primary contact for a partner."""
        result = await self._session.execute(
            select(ContactModel).where(
                ContactModel.partner_id == partner_id,
                ContactModel.is_primary == True,  # noqa: E712
            )
        )
        model = result.scalar_one_or_none()
        return ContactMapper.to_entity(model) if model else None

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> list[Contact]:
        """List contacts with optional filters."""
        query = select(ContactModel)

        if is_active is not None:
            query = query.where(ContactModel.is_active == is_active)

        query = query.order_by(ContactModel.last_name).offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [ContactMapper.to_entity(model) for model in models]

    async def save(self, contact: Contact) -> Contact:
        """Save (create or update) contact."""
        result = await self._session.execute(
            select(ContactModel).where(ContactModel.id == contact.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            ContactMapper.update_model(existing, contact)
            await self._session.flush()
            return ContactMapper.to_entity(existing)
        else:
            model = ContactMapper.to_model(contact)
            self._session.add(model)
            await self._session.flush()
            return ContactMapper.to_entity(model)

    async def delete(self, contact_id: str) -> bool:
        """Delete contact."""
        result = await self._session.execute(
            select(ContactModel).where(ContactModel.id == contact_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def count(self, partner_id: str | None = None) -> int:
        """Count contacts, optionally for a specific partner."""
        query = select(func.count(ContactModel.id))

        if partner_id is not None:
            query = query.where(ContactModel.partner_id == partner_id)

        result = await self._session.execute(query)
        return result.scalar() or 0


class PostgresLeadRepository(ILeadRepository):
    """PostgreSQL implementation of Lead repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, lead_id: str) -> Lead | None:
        """Get lead by ID."""
        result = await self._session.execute(
            select(LeadModel).where(LeadModel.id == lead_id)
        )
        model = result.scalar_one_or_none()
        return LeadMapper.to_entity(model) if model else None

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[Lead]:
        """List leads with optional filters."""
        query = select(LeadModel)

        if status is not None:
            query = query.where(LeadModel.status == status)

        query = query.order_by(LeadModel.created_at.desc()).offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [LeadMapper.to_entity(model) for model in models]

    async def search(self, query: str) -> list[Lead]:
        """Search leads by name, company, email, or other fields."""
        search_pattern = f"%{query}%"
        stmt = (
            select(LeadModel)
            .where(
                or_(
                    LeadModel.name.ilike(search_pattern),
                    LeadModel.company.ilike(search_pattern),
                    LeadModel.email.ilike(search_pattern),
                )
            )
            .order_by(LeadModel.created_at.desc())
            .limit(50)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [LeadMapper.to_entity(model) for model in models]

    async def save(self, lead: Lead) -> Lead:
        """Save (create or update) lead."""
        result = await self._session.execute(
            select(LeadModel).where(LeadModel.id == lead.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            LeadMapper.update_model(existing, lead)
            await self._session.flush()
            return LeadMapper.to_entity(existing)
        else:
            model = LeadMapper.to_model(lead)
            self._session.add(model)
            await self._session.flush()
            return LeadMapper.to_entity(model)

    async def delete(self, lead_id: str) -> bool:
        """Delete lead."""
        result = await self._session.execute(
            select(LeadModel).where(LeadModel.id == lead_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def count(self, status: str | None = None) -> int:
        """Count leads with optional filters."""
        query = select(func.count(LeadModel.id))

        if status is not None:
            query = query.where(LeadModel.status == status)

        result = await self._session.execute(query)
        return result.scalar() or 0


class PostgresOpportunityRepository(IOpportunityRepository):
    """PostgreSQL implementation of Opportunity repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, opportunity_id: str) -> Opportunity | None:
        """Get opportunity by ID."""
        result = await self._session.execute(
            select(OpportunityModel).where(OpportunityModel.id == opportunity_id)
        )
        model = result.scalar_one_or_none()
        return OpportunityMapper.to_entity(model) if model else None

    async def get_by_partner_id(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Opportunity]:
        """Get opportunities for a specific partner."""
        query = (
            select(OpportunityModel)
            .where(OpportunityModel.partner_id == partner_id)
            .order_by(OpportunityModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [OpportunityMapper.to_entity(model) for model in models]

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        stage: str | None = None,
    ) -> list[Opportunity]:
        """List opportunities with optional filters."""
        query = select(OpportunityModel)

        if stage is not None:
            query = query.where(OpportunityModel.stage == stage)

        query = (
            query.order_by(OpportunityModel.expected_close_date).offset(skip).limit(limit)
        )

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [OpportunityMapper.to_entity(model) for model in models]

    async def save(self, opportunity: Opportunity) -> Opportunity:
        """Save (create or update) opportunity."""
        result = await self._session.execute(
            select(OpportunityModel).where(OpportunityModel.id == opportunity.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            OpportunityMapper.update_model(existing, opportunity)
            await self._session.flush()
            return OpportunityMapper.to_entity(existing)
        else:
            model = OpportunityMapper.to_model(opportunity)
            self._session.add(model)
            await self._session.flush()
            return OpportunityMapper.to_entity(model)

    async def delete(self, opportunity_id: str) -> bool:
        """Delete opportunity."""
        result = await self._session.execute(
            select(OpportunityModel).where(OpportunityModel.id == opportunity_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def count(
        self, partner_id: str | None = None, stage: str | None = None
    ) -> int:
        """Count opportunities with optional filters."""
        query = select(func.count(OpportunityModel.id))

        if partner_id is not None:
            query = query.where(OpportunityModel.partner_id == partner_id)
        if stage is not None:
            query = query.where(OpportunityModel.stage == stage)

        result = await self._session.execute(query)
        return result.scalar() or 0
