"""
FastAPI routes for CRM module.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

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
from serp_crm.application.services import (
    ContactService,
    LeadService,
    OpportunityService,
    PartnerService,
)
from serp_crm.infrastructure.repositories import (
    InMemoryContactRepository,
    InMemoryLeadRepository,
    InMemoryOpportunityRepository,
    InMemoryPartnerRepository,
)

# Create router
router = APIRouter(prefix="/api/crm", tags=["CRM"])

# Repository singletons (in production, use dependency injection)
_partner_repo = InMemoryPartnerRepository()
_contact_repo = InMemoryContactRepository()
_lead_repo = InMemoryLeadRepository()
_opportunity_repo = InMemoryOpportunityRepository()


# Dependency injection
def get_partner_service() -> PartnerService:
    """Get Partner service."""
    return PartnerService(_partner_repo)


def get_contact_service() -> ContactService:
    """Get Contact service."""
    return ContactService(_contact_repo, _partner_repo)


def get_lead_service() -> LeadService:
    """Get Lead service."""
    return LeadService(_lead_repo, _partner_repo, _contact_repo)


def get_opportunity_service() -> OpportunityService:
    """Get Opportunity service."""
    return OpportunityService(_opportunity_repo, _partner_repo)


# ===== PARTNER ROUTES =====


@router.post(
    "/partners",
    response_model=PartnerDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new partner",
)
async def create_partner(
    dto: PartnerCreateDTO,
    service: PartnerService = Depends(get_partner_service),
) -> PartnerDTO:
    """Create a new partner (customer, supplier, or both)."""
    return await service.create_partner(dto)


@router.get(
    "/partners",
    response_model=PartnerListDTO,
    summary="List partners",
)
async def list_partners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_customer: bool | None = None,
    is_supplier: bool | None = None,
    is_active: bool | None = None,
    service: PartnerService = Depends(get_partner_service),
) -> PartnerListDTO:
    """List partners with optional filters."""
    return await service.list_partners(
        skip=skip,
        limit=limit,
        is_customer=is_customer,
        is_supplier=is_supplier,
        is_active=is_active,
    )


@router.get(
    "/partners/search",
    response_model=list[PartnerDTO],
    summary="Search partners",
)
async def search_partners(
    q: str = Query(..., min_length=1),
    service: PartnerService = Depends(get_partner_service),
) -> list[PartnerDTO]:
    """Search partners by name, email, or other fields."""
    return await service.search_partners(q)


@router.get(
    "/partners/{partner_id}",
    response_model=PartnerDTO,
    summary="Get partner by ID",
)
async def get_partner(
    partner_id: str,
    service: PartnerService = Depends(get_partner_service),
) -> PartnerDTO:
    """Get partner details by ID."""
    partner = await service.get_partner(partner_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    return partner


@router.put(
    "/partners/{partner_id}",
    response_model=PartnerDTO,
    summary="Update partner",
)
async def update_partner(
    partner_id: str,
    dto: PartnerUpdateDTO,
    service: PartnerService = Depends(get_partner_service),
) -> PartnerDTO:
    """Update an existing partner."""
    partner = await service.update_partner(partner_id, dto)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    return partner


@router.delete(
    "/partners/{partner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete partner",
)
async def delete_partner(
    partner_id: str,
    service: PartnerService = Depends(get_partner_service),
) -> None:
    """Delete a partner."""
    deleted = await service.delete_partner(partner_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )


@router.get(
    "/partners/{partner_id}/contacts",
    response_model=ContactListDTO,
    summary="Get partner contacts",
)
async def get_partner_contacts(
    partner_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: ContactService = Depends(get_contact_service),
) -> ContactListDTO:
    """Get all contacts for a partner."""
    return await service.get_partner_contacts(partner_id, skip=skip, limit=limit)


@router.get(
    "/partners/{partner_id}/opportunities",
    response_model=OpportunityListDTO,
    summary="Get partner opportunities",
)
async def get_partner_opportunities(
    partner_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: OpportunityService = Depends(get_opportunity_service),
) -> OpportunityListDTO:
    """Get all opportunities for a partner."""
    return await service.get_partner_opportunities(partner_id, skip=skip, limit=limit)


# ===== CONTACT ROUTES =====


@router.post(
    "/contacts",
    response_model=ContactDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact",
)
async def create_contact(
    dto: ContactCreateDTO,
    service: ContactService = Depends(get_contact_service),
) -> ContactDTO:
    """Create a new contact for a partner."""
    try:
        return await service.create_contact(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/contacts",
    response_model=ContactListDTO,
    summary="List contacts",
)
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: bool | None = None,
    service: ContactService = Depends(get_contact_service),
) -> ContactListDTO:
    """List all contacts."""
    return await service.list_contacts(skip=skip, limit=limit, is_active=is_active)


@router.get(
    "/contacts/{contact_id}",
    response_model=ContactDTO,
    summary="Get contact by ID",
)
async def get_contact(
    contact_id: str,
    service: ContactService = Depends(get_contact_service),
) -> ContactDTO:
    """Get contact details by ID."""
    contact = await service.get_contact(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} not found",
        )
    return contact


@router.put(
    "/contacts/{contact_id}",
    response_model=ContactDTO,
    summary="Update contact",
)
async def update_contact(
    contact_id: str,
    dto: ContactUpdateDTO,
    service: ContactService = Depends(get_contact_service),
) -> ContactDTO:
    """Update an existing contact."""
    contact = await service.update_contact(contact_id, dto)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} not found",
        )
    return contact


@router.delete(
    "/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact",
)
async def delete_contact(
    contact_id: str,
    service: ContactService = Depends(get_contact_service),
) -> None:
    """Delete a contact."""
    deleted = await service.delete_contact(contact_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} not found",
        )


# ===== LEAD ROUTES =====


@router.post(
    "/leads",
    response_model=LeadDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lead",
)
async def create_lead(
    dto: LeadCreateDTO,
    service: LeadService = Depends(get_lead_service),
) -> LeadDTO:
    """Create a new lead."""
    return await service.create_lead(dto)


@router.get(
    "/leads",
    response_model=LeadListDTO,
    summary="List leads",
)
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None, regex="^(NEW|CONTACTED|QUALIFIED|LOST)$"),
    service: LeadService = Depends(get_lead_service),
) -> LeadListDTO:
    """List leads with optional status filter."""
    return await service.list_leads(skip=skip, limit=limit, status=status)


@router.get(
    "/leads/{lead_id}",
    response_model=LeadDTO,
    summary="Get lead by ID",
)
async def get_lead(
    lead_id: str,
    service: LeadService = Depends(get_lead_service),
) -> LeadDTO:
    """Get lead details by ID."""
    lead = await service.get_lead(lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} not found",
        )
    return lead


@router.put(
    "/leads/{lead_id}",
    response_model=LeadDTO,
    summary="Update lead",
)
async def update_lead(
    lead_id: str,
    dto: LeadUpdateDTO,
    service: LeadService = Depends(get_lead_service),
) -> LeadDTO:
    """Update an existing lead."""
    lead = await service.update_lead(lead_id, dto)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} not found",
        )
    return lead


@router.post(
    "/leads/{lead_id}/contact",
    response_model=LeadDTO,
    summary="Mark lead as contacted",
)
async def contact_lead(
    lead_id: str,
    service: LeadService = Depends(get_lead_service),
) -> LeadDTO:
    """Mark a lead as contacted."""
    try:
        lead = await service.contact_lead(lead_id)
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead {lead_id} not found",
            )
        return lead
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/leads/{lead_id}/qualify",
    response_model=dict,
    summary="Qualify lead and convert to partner",
)
async def qualify_lead(
    lead_id: str,
    dto: LeadQualifyDTO = LeadQualifyDTO(),
    service: LeadService = Depends(get_lead_service),
) -> dict:
    """Qualify a lead and convert it to a partner."""
    try:
        partner, contact = await service.qualify_lead(lead_id, dto)
        return {
            "partner": partner.model_dump(),
            "contact": contact.model_dump() if contact else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/leads/{lead_id}/lose",
    response_model=LeadDTO,
    summary="Mark lead as lost",
)
async def lose_lead(
    lead_id: str,
    service: LeadService = Depends(get_lead_service),
) -> LeadDTO:
    """Mark a lead as lost."""
    try:
        lead = await service.lose_lead(lead_id)
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead {lead_id} not found",
            )
        return lead
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/leads/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lead",
)
async def delete_lead(
    lead_id: str,
    service: LeadService = Depends(get_lead_service),
) -> None:
    """Delete a lead."""
    deleted = await service.delete_lead(lead_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} not found",
        )


# ===== OPPORTUNITY ROUTES =====


@router.post(
    "/opportunities",
    response_model=OpportunityDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new opportunity",
)
async def create_opportunity(
    dto: OpportunityCreateDTO,
    service: OpportunityService = Depends(get_opportunity_service),
) -> OpportunityDTO:
    """Create a new opportunity."""
    try:
        return await service.create_opportunity(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/opportunities",
    response_model=OpportunityListDTO,
    summary="List opportunities",
)
async def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    stage: str | None = Query(
        None, regex="^(PROSPECTING|QUALIFICATION|PROPOSAL|NEGOTIATION|WON|LOST)$"
    ),
    service: OpportunityService = Depends(get_opportunity_service),
) -> OpportunityListDTO:
    """List opportunities with optional stage filter."""
    return await service.list_opportunities(skip=skip, limit=limit, stage=stage)


@router.get(
    "/opportunities/{opportunity_id}",
    response_model=OpportunityDTO,
    summary="Get opportunity by ID",
)
async def get_opportunity(
    opportunity_id: str,
    service: OpportunityService = Depends(get_opportunity_service),
) -> OpportunityDTO:
    """Get opportunity details by ID."""
    opportunity = await service.get_opportunity(opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found",
        )
    return opportunity


@router.put(
    "/opportunities/{opportunity_id}",
    response_model=OpportunityDTO,
    summary="Update opportunity",
)
async def update_opportunity(
    opportunity_id: str,
    dto: OpportunityUpdateDTO,
    service: OpportunityService = Depends(get_opportunity_service),
) -> OpportunityDTO:
    """Update an existing opportunity."""
    try:
        opportunity = await service.update_opportunity(opportunity_id, dto)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity {opportunity_id} not found",
            )
        return opportunity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/opportunities/{opportunity_id}/win",
    response_model=OpportunityDTO,
    summary="Mark opportunity as won",
)
async def win_opportunity(
    opportunity_id: str,
    service: OpportunityService = Depends(get_opportunity_service),
) -> OpportunityDTO:
    """Mark an opportunity as won."""
    try:
        opportunity = await service.win_opportunity(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity {opportunity_id} not found",
            )
        return opportunity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/opportunities/{opportunity_id}/lose",
    response_model=OpportunityDTO,
    summary="Mark opportunity as lost",
)
async def lose_opportunity(
    opportunity_id: str,
    service: OpportunityService = Depends(get_opportunity_service),
) -> OpportunityDTO:
    """Mark an opportunity as lost."""
    try:
        opportunity = await service.lose_opportunity(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity {opportunity_id} not found",
            )
        return opportunity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/opportunities/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete opportunity",
)
async def delete_opportunity(
    opportunity_id: str,
    service: OpportunityService = Depends(get_opportunity_service),
) -> None:
    """Delete an opportunity."""
    deleted = await service.delete_opportunity(opportunity_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found",
        )
