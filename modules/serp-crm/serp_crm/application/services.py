"""
Application services for CRM module.

Application services orchestrate domain logic, manage transactions,
and handle DTO conversions.
"""

from datetime import datetime

from serp_crm.application.dto import (
    ContactCreateDTO,
    ContactDTO,
    ContactListDTO,
    ContactUpdateDTO,
    LeadCreateDTO,
    LeadDTO,
    LeadListDTO,
    LeadQualifyDTO,
    LeadUpdateDTO,
    OpportunityCreateDTO,
    OpportunityDTO,
    OpportunityListDTO,
    OpportunityUpdateDTO,
    PartnerCreateDTO,
    PartnerDTO,
    PartnerListDTO,
    PartnerUpdateDTO,
)
from serp_crm.domain.entities import (
    Contact,
    Lead,
    Opportunity,
    OpportunityStage,
    Partner,
    PartnerType,
)
from serp_crm.domain.repositories import (
    IContactRepository,
    ILeadRepository,
    IOpportunityRepository,
    IPartnerRepository,
)
from serp_crm.domain.services import LeadConversionService
from serp_crm.domain.value_objects import Address, Email, Money, PhoneNumber, TaxId


class PartnerService:
    """Application service for Partner management."""

    def __init__(self, partner_repository: IPartnerRepository):
        self.partner_repository = partner_repository

    async def create_partner(self, dto: PartnerCreateDTO) -> PartnerDTO:
        """Create a new partner."""
        # Build address if provided
        billing_address = None
        if dto.street and dto.city and dto.country:
            billing_address = Address(
                street=dto.street,
                city=dto.city,
                state=dto.state,
                postal_code=dto.postal_code or "",
                country=dto.country,
            )

        # Build value objects
        email = Email(dto.email) if dto.email else None
        phone = PhoneNumber(dto.phone) if dto.phone else None
        tax_id = TaxId(dto.tax_id, dto.country) if dto.tax_id and dto.country else None

        annual_revenue = None
        if dto.annual_revenue_amount and dto.annual_revenue_currency:
            annual_revenue = Money(
                dto.annual_revenue_amount, dto.annual_revenue_currency
            )

        # Create entity
        partner = Partner(
            name=dto.name,
            partner_type=PartnerType(dto.partner_type),
            is_customer=dto.is_customer,
            is_supplier=dto.is_supplier,
            email=email,
            phone=phone,
            website=dto.website,
            billing_address=billing_address,
            tax_id=tax_id,
            company_registry=dto.company_registry,
            industry=dto.industry,
            employee_count=dto.employee_count,
            annual_revenue=annual_revenue,
            notes=dto.notes,
            tags=dto.tags,
        )

        # Save
        partner = await self.partner_repository.save(partner)

        # Return DTO
        return self._to_dto(partner)

    async def get_partner(self, partner_id: str) -> PartnerDTO | None:
        """Get partner by ID."""
        partner = await self.partner_repository.get_by_id(partner_id)
        return self._to_dto(partner) if partner else None

    async def list_partners(
        self,
        skip: int = 0,
        limit: int = 100,
        is_customer: bool | None = None,
        is_supplier: bool | None = None,
        is_active: bool | None = None,
    ) -> PartnerListDTO:
        """List partners with filters."""
        partners = await self.partner_repository.list_all(
            skip=skip,
            limit=limit,
            is_customer=is_customer,
            is_supplier=is_supplier,
            is_active=is_active,
        )
        total = await self.partner_repository.count(
            is_customer=is_customer,
            is_supplier=is_supplier,
            is_active=is_active,
        )

        return PartnerListDTO(
            partners=[self._to_dto(p) for p in partners],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_partner(
        self, partner_id: str, dto: PartnerUpdateDTO
    ) -> PartnerDTO | None:
        """Update an existing partner."""
        partner = await self.partner_repository.get_by_id(partner_id)
        if not partner:
            return None

        # Update fields
        if dto.name is not None:
            partner.name = dto.name
        if dto.is_customer is not None:
            partner.is_customer = dto.is_customer
        if dto.is_supplier is not None:
            partner.is_supplier = dto.is_supplier
        if dto.email is not None:
            partner.email = Email(dto.email) if dto.email else None
        if dto.phone is not None:
            partner.phone = PhoneNumber(dto.phone) if dto.phone else None
        if dto.website is not None:
            partner.website = dto.website

        # Update address if provided
        if any([dto.street, dto.city, dto.country]):
            if dto.street and dto.city and dto.country:
                partner.billing_address = Address(
                    street=dto.street,
                    city=dto.city,
                    state=dto.state,
                    postal_code=dto.postal_code or "",
                    country=dto.country,
                )

        if dto.tax_id is not None and dto.country is not None:
            partner.tax_id = TaxId(dto.tax_id, dto.country) if dto.tax_id else None

        if dto.industry is not None:
            partner.industry = dto.industry
        if dto.employee_count is not None:
            partner.employee_count = dto.employee_count
        if dto.notes is not None:
            partner.notes = dto.notes
        if dto.tags is not None:
            partner.tags = dto.tags

        partner.updated_at = datetime.now()

        # Save
        partner = await self.partner_repository.save(partner)

        return self._to_dto(partner)

    async def delete_partner(self, partner_id: str) -> bool:
        """Delete a partner."""
        return await self.partner_repository.delete(partner_id)

    async def search_partners(self, query: str) -> list[PartnerDTO]:
        """Search partners."""
        partners = await self.partner_repository.search(query)
        return [self._to_dto(p) for p in partners]

    def _to_dto(self, partner: Partner) -> PartnerDTO:
        """Convert entity to DTO."""
        return PartnerDTO(**partner.to_dict())


class ContactService:
    """Application service for Contact management."""

    def __init__(
        self,
        contact_repository: IContactRepository,
        partner_repository: IPartnerRepository,
    ):
        self.contact_repository = contact_repository
        self.partner_repository = partner_repository

    async def create_contact(self, dto: ContactCreateDTO) -> ContactDTO:
        """Create a new contact."""
        # Verify partner exists
        partner = await self.partner_repository.get_by_id(dto.partner_id)
        if not partner:
            raise ValueError(f"Partner {dto.partner_id} not found")

        # Build value objects
        email = Email(dto.email) if dto.email else None
        phone = PhoneNumber(dto.phone) if dto.phone else None
        mobile = PhoneNumber(dto.mobile) if dto.mobile else None

        address = None
        if dto.street and dto.city and dto.country:
            address = Address(
                street=dto.street,
                city=dto.city,
                state=dto.state,
                postal_code=dto.postal_code or "",
                country=dto.country,
            )

        # Handle primary contact logic
        if dto.is_primary:
            # Unset other primary contacts for this partner
            existing_primary = await self.contact_repository.get_primary_contact(
                dto.partner_id
            )
            if existing_primary:
                existing_primary.unset_as_primary()
                await self.contact_repository.save(existing_primary)

        # Create entity
        contact = Contact(
            partner_id=dto.partner_id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            is_primary=dto.is_primary,
            email=email,
            phone=phone,
            mobile=mobile,
            job_title=dto.job_title,
            department=dto.department,
            address=address,
            notes=dto.notes,
            tags=dto.tags,
        )

        # Save
        contact = await self.contact_repository.save(contact)

        return self._to_dto(contact)

    async def get_contact(self, contact_id: str) -> ContactDTO | None:
        """Get contact by ID."""
        contact = await self.contact_repository.get_by_id(contact_id)
        return self._to_dto(contact) if contact else None

    async def get_partner_contacts(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> ContactListDTO:
        """Get all contacts for a partner."""
        contacts = await self.contact_repository.get_by_partner_id(
            partner_id, skip=skip, limit=limit
        )
        total = await self.contact_repository.count(partner_id=partner_id)

        return ContactListDTO(
            contacts=[self._to_dto(c) for c in contacts],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def list_contacts(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> ContactListDTO:
        """List all contacts."""
        contacts = await self.contact_repository.list_all(
            skip=skip, limit=limit, is_active=is_active
        )
        total = await self.contact_repository.count()

        return ContactListDTO(
            contacts=[self._to_dto(c) for c in contacts],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_contact(
        self, contact_id: str, dto: ContactUpdateDTO
    ) -> ContactDTO | None:
        """Update an existing contact."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            return None

        # Update fields
        if dto.first_name is not None:
            contact.first_name = dto.first_name
        if dto.last_name is not None:
            contact.last_name = dto.last_name
        if dto.email is not None:
            contact.email = Email(dto.email) if dto.email else None
        if dto.phone is not None:
            contact.phone = PhoneNumber(dto.phone) if dto.phone else None
        if dto.mobile is not None:
            contact.mobile = PhoneNumber(dto.mobile) if dto.mobile else None
        if dto.job_title is not None:
            contact.job_title = dto.job_title
        if dto.department is not None:
            contact.department = dto.department
        if dto.notes is not None:
            contact.notes = dto.notes
        if dto.tags is not None:
            contact.tags = dto.tags

        # Handle primary contact
        if dto.is_primary is not None and dto.is_primary != contact.is_primary:
            if dto.is_primary:
                # Unset other primary contacts
                existing_primary = await self.contact_repository.get_primary_contact(
                    contact.partner_id
                )
                if existing_primary and existing_primary.id != contact.id:
                    existing_primary.unset_as_primary()
                    await self.contact_repository.save(existing_primary)
                contact.set_as_primary()
            else:
                contact.unset_as_primary()

        contact.updated_at = datetime.now()

        # Save
        contact = await self.contact_repository.save(contact)

        return self._to_dto(contact)

    async def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact."""
        return await self.contact_repository.delete(contact_id)

    def _to_dto(self, contact: Contact) -> ContactDTO:
        """Convert entity to DTO."""
        return ContactDTO(**contact.to_dict())


class LeadService:
    """Application service for Lead management."""

    def __init__(
        self,
        lead_repository: ILeadRepository,
        partner_repository: IPartnerRepository,
        contact_repository: IContactRepository,
    ):
        self.lead_repository = lead_repository
        self.partner_repository = partner_repository
        self.contact_repository = contact_repository
        self.conversion_service = LeadConversionService(
            partner_repository, contact_repository
        )

    async def create_lead(self, dto: LeadCreateDTO) -> LeadDTO:
        """Create a new lead."""
        email = Email(dto.email) if dto.email else None
        phone = PhoneNumber(dto.phone) if dto.phone else None

        lead = Lead(
            name=dto.name,
            company=dto.company,
            email=email,
            phone=phone,
            source=dto.source,
            score=dto.score,
            interest_level=dto.interest_level,
            notes=dto.notes,
            tags=dto.tags,
        )

        lead = await self.lead_repository.save(lead)

        return self._to_dto(lead)

    async def get_lead(self, lead_id: str) -> LeadDTO | None:
        """Get lead by ID."""
        lead = await self.lead_repository.get_by_id(lead_id)
        return self._to_dto(lead) if lead else None

    async def list_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> LeadListDTO:
        """List leads."""
        leads = await self.lead_repository.list_all(
            skip=skip, limit=limit, status=status
        )
        total = await self.lead_repository.count(status=status)

        return LeadListDTO(
            leads=[self._to_dto(lead) for lead in leads],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_lead(self, lead_id: str, dto: LeadUpdateDTO) -> LeadDTO | None:
        """Update an existing lead."""
        lead = await self.lead_repository.get_by_id(lead_id)
        if not lead:
            return None

        if dto.name is not None:
            lead.name = dto.name
        if dto.company is not None:
            lead.company = dto.company
        if dto.email is not None:
            lead.email = Email(dto.email) if dto.email else None
        if dto.phone is not None:
            lead.phone = PhoneNumber(dto.phone) if dto.phone else None
        if dto.source is not None:
            lead.source = dto.source
        if dto.score is not None:
            lead.update_score(dto.score)
        if dto.interest_level is not None:
            lead.interest_level = dto.interest_level
        if dto.notes is not None:
            lead.notes = dto.notes
        if dto.tags is not None:
            lead.tags = dto.tags

        lead.updated_at = datetime.now()

        lead = await self.lead_repository.save(lead)

        return self._to_dto(lead)

    async def contact_lead(self, lead_id: str) -> LeadDTO | None:
        """Mark lead as contacted."""
        lead = await self.lead_repository.get_by_id(lead_id)
        if not lead:
            return None

        lead.contact()
        lead = await self.lead_repository.save(lead)

        return self._to_dto(lead)

    async def qualify_lead(
        self, lead_id: str, dto: LeadQualifyDTO
    ) -> tuple[PartnerDTO, ContactDTO | None]:
        """Qualify lead and convert to partner."""
        lead = await self.lead_repository.get_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        # Qualify the lead
        lead.qualify()

        # Convert to partner using domain service
        partner, contact = await self.conversion_service.convert_lead_to_partner(
            lead, create_contact=dto.create_contact
        )

        # Save lead
        await self.lead_repository.save(lead)

        # Convert to DTOs
        partner_dto = PartnerDTO(**partner.to_dict())
        contact_dto = ContactDTO(**contact.to_dict()) if contact else None

        return partner_dto, contact_dto

    async def lose_lead(self, lead_id: str) -> LeadDTO | None:
        """Mark lead as lost."""
        lead = await self.lead_repository.get_by_id(lead_id)
        if not lead:
            return None

        lead.lose()
        lead = await self.lead_repository.save(lead)

        return self._to_dto(lead)

    async def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead."""
        return await self.lead_repository.delete(lead_id)

    def _to_dto(self, lead: Lead) -> LeadDTO:
        """Convert entity to DTO."""
        return LeadDTO(**lead.to_dict())


class OpportunityService:
    """Application service for Opportunity management."""

    def __init__(
        self,
        opportunity_repository: IOpportunityRepository,
        partner_repository: IPartnerRepository,
    ):
        self.opportunity_repository = opportunity_repository
        self.partner_repository = partner_repository

    async def create_opportunity(self, dto: OpportunityCreateDTO) -> OpportunityDTO:
        """Create a new opportunity."""
        # Verify partner exists
        partner = await self.partner_repository.get_by_id(dto.partner_id)
        if not partner:
            raise ValueError(f"Partner {dto.partner_id} not found")

        amount = Money(dto.amount, dto.currency) if dto.amount else None

        opportunity = Opportunity(
            partner_id=dto.partner_id,
            name=dto.name,
            amount=amount,
            probability=dto.probability,
            expected_close_date=dto.expected_close_date,
            source=dto.source,
            campaign=dto.campaign,
            notes=dto.notes,
            tags=dto.tags,
        )

        opportunity = await self.opportunity_repository.save(opportunity)

        return self._to_dto(opportunity)

    async def get_opportunity(self, opportunity_id: str) -> OpportunityDTO | None:
        """Get opportunity by ID."""
        opportunity = await self.opportunity_repository.get_by_id(opportunity_id)
        return self._to_dto(opportunity) if opportunity else None

    async def get_partner_opportunities(
        self, partner_id: str, skip: int = 0, limit: int = 100
    ) -> OpportunityListDTO:
        """Get all opportunities for a partner."""
        opportunities = await self.opportunity_repository.get_by_partner_id(
            partner_id, skip=skip, limit=limit
        )
        total = await self.opportunity_repository.count(partner_id=partner_id)

        return OpportunityListDTO(
            opportunities=[self._to_dto(o) for o in opportunities],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def list_opportunities(
        self,
        skip: int = 0,
        limit: int = 100,
        stage: str | None = None,
    ) -> OpportunityListDTO:
        """List all opportunities."""
        opportunities = await self.opportunity_repository.list_all(
            skip=skip, limit=limit, stage=stage
        )
        total = await self.opportunity_repository.count(stage=stage)

        return OpportunityListDTO(
            opportunities=[self._to_dto(o) for o in opportunities],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_opportunity(
        self, opportunity_id: str, dto: OpportunityUpdateDTO
    ) -> OpportunityDTO | None:
        """Update an existing opportunity."""
        opportunity = await self.opportunity_repository.get_by_id(opportunity_id)
        if not opportunity:
            return None

        if dto.name is not None:
            opportunity.name = dto.name
        if dto.stage is not None:
            opportunity.move_to_stage(OpportunityStage(dto.stage))
        if dto.amount is not None and dto.currency is not None:
            opportunity.update_amount(Money(dto.amount, dto.currency))
        if dto.probability is not None:
            opportunity.update_probability(dto.probability)
        if dto.expected_close_date is not None:
            opportunity.expected_close_date = dto.expected_close_date
        if dto.source is not None:
            opportunity.source = dto.source
        if dto.campaign is not None:
            opportunity.campaign = dto.campaign
        if dto.notes is not None:
            opportunity.notes = dto.notes
        if dto.tags is not None:
            opportunity.tags = dto.tags

        opportunity.updated_at = datetime.now()

        opportunity = await self.opportunity_repository.save(opportunity)

        return self._to_dto(opportunity)

    async def win_opportunity(self, opportunity_id: str) -> OpportunityDTO | None:
        """Mark opportunity as won."""
        opportunity = await self.opportunity_repository.get_by_id(opportunity_id)
        if not opportunity:
            return None

        opportunity.win()
        opportunity = await self.opportunity_repository.save(opportunity)

        return self._to_dto(opportunity)

    async def lose_opportunity(self, opportunity_id: str) -> OpportunityDTO | None:
        """Mark opportunity as lost."""
        opportunity = await self.opportunity_repository.get_by_id(opportunity_id)
        if not opportunity:
            return None

        opportunity.lose()
        opportunity = await self.opportunity_repository.save(opportunity)

        return self._to_dto(opportunity)

    async def delete_opportunity(self, opportunity_id: str) -> bool:
        """Delete an opportunity."""
        return await self.opportunity_repository.delete(opportunity_id)

    def _to_dto(self, opportunity: Opportunity) -> OpportunityDTO:
        """Convert entity to DTO."""
        return OpportunityDTO(**opportunity.to_dict())
