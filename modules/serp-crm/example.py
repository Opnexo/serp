"""
Example usage of the SERP CRM module.

This script demonstrates the key features of the CRM module:
- Creating partners (customers/suppliers)
- Managing contacts
- Lead qualification and conversion
- Opportunity tracking
"""

import asyncio
from decimal import Decimal

from serp_crm.application.dto import (
    ContactCreateDTO,
    LeadCreateDTO,
    LeadQualifyDTO,
    OpportunityCreateDTO,
    PartnerCreateDTO,
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


async def main():
    """Run CRM examples."""
    print("=" * 60)
    print("SERP CRM Module - Example Usage")
    print("=" * 60)

    # Initialize repositories
    partner_repo = InMemoryPartnerRepository()
    contact_repo = InMemoryContactRepository()
    lead_repo = InMemoryLeadRepository()
    opportunity_repo = InMemoryOpportunityRepository()

    # Initialize services
    partner_service = PartnerService(partner_repo)
    contact_service = ContactService(contact_repo, partner_repo)
    lead_service = LeadService(lead_repo, partner_repo, contact_repo)
    opportunity_service = OpportunityService(opportunity_repo, partner_repo)

    # ===== EXAMPLE 1: Create a Partner (Customer) =====
    print("\n1. Creating a customer partner...")
    partner_dto = PartnerCreateDTO(
        name="Acme Corporation",
        partner_type="COMPANY",
        is_customer=True,
        email="contact@acme.com",
        phone="+1-555-0100",
        website="https://acme.com",
        street="123 Business Ave",
        city="New York",
        state="NY",
        postal_code="10001",
        country="US",
        industry="Technology",
        employee_count=500,
        notes="Major enterprise customer",
        tags=["enterprise", "technology"],
    )

    partner = await partner_service.create_partner(partner_dto)
    print(f"✓ Created partner: {partner.name} (ID: {partner.id})")
    print(f"  - Type: {partner.partner_type}")
    print(f"  - Customer: {partner.is_customer}")
    print(f"  - Email: {partner.email}")

    # ===== EXAMPLE 2: Create Contacts for Partner =====
    print("\n2. Creating contacts for the partner...")

    # Primary contact
    contact1_dto = ContactCreateDTO(
        partner_id=partner.id,
        first_name="John",
        last_name="Doe",
        email="john.doe@acme.com",
        phone="+1-555-0101",
        job_title="CEO",
        is_primary=True,
    )
    contact1 = await contact_service.create_contact(contact1_dto)
    print(f"✓ Created primary contact: {contact1.full_name}")
    print(f"  - Title: {contact1.job_title}")
    print(f"  - Email: {contact1.email}")

    # Secondary contact
    contact2_dto = ContactCreateDTO(
        partner_id=partner.id,
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@acme.com",
        phone="+1-555-0102",
        job_title="CTO",
        is_primary=False,
    )
    contact2 = await contact_service.create_contact(contact2_dto)
    print(f"✓ Created contact: {contact2.full_name}")
    print(f"  - Title: {contact2.job_title}")

    # ===== EXAMPLE 3: Lead Management =====
    print("\n3. Managing leads...")

    # Create a lead
    lead_dto = LeadCreateDTO(
        name="Bob Wilson",
        company="Tech Startup Inc",
        email="bob@techstartup.io",
        phone="+1-555-0200",
        source="Website",
        score=75,
        interest_level="High",
        notes="Interested in enterprise plan",
    )
    lead = await lead_service.create_lead(lead_dto)
    print(f"✓ Created lead: {lead.name}")
    print(f"  - Company: {lead.company}")
    print(f"  - Score: {lead.score}")
    print(f"  - Status: {lead.status}")

    # Contact the lead
    lead = await lead_service.contact_lead(lead.id)
    print("✓ Marked lead as contacted")
    print(f"  - Status: {lead.status}")

    # Qualify and convert lead to partner
    print("\n4. Converting qualified lead to partner...")
    converted = await lead_service.qualify_lead(
        lead.id, LeadQualifyDTO(create_contact=True)
    )
    new_partner = converted[0]
    new_contact = converted[1]
    print(f"✓ Lead converted to partner: {new_partner.name}")
    if new_contact:
        print(f"  - Contact created: {new_contact.full_name}")

    # ===== EXAMPLE 5: Opportunity Tracking =====
    print("\n5. Creating and tracking opportunities...")

    # Create opportunity for our original partner
    opp_dto = OpportunityCreateDTO(
        partner_id=partner.id,
        name="Annual Software License Renewal",
        amount=Decimal("150000.00"),
        currency="USD",
        probability=80,
        expected_close_date="2025-12-31",
        source="Existing Customer",
        campaign="Renewal Campaign 2025",
        notes="High-value renewal opportunity",
    )
    opportunity = await opportunity_service.create_opportunity(opp_dto)
    print(f"✓ Created opportunity: {opportunity.name}")
    print(f"  - Amount: {opportunity.amount}")
    print(f"  - Probability: {opportunity.probability}%")
    print(f"  - Expected Value: {opportunity.expected_value}")
    print(f"  - Stage: {opportunity.stage}")

    # Move through stages
    from serp_crm.application.dto import OpportunityUpdateDTO

    # Move to proposal stage
    await opportunity_service.update_opportunity(
        opportunity.id, OpportunityUpdateDTO(stage="PROPOSAL")
    )
    print("✓ Moved to PROPOSAL stage")

    # Move to negotiation
    await opportunity_service.update_opportunity(
        opportunity.id, OpportunityUpdateDTO(stage="NEGOTIATION")
    )
    print("✓ Moved to NEGOTIATION stage")

    # Win the opportunity
    opportunity = await opportunity_service.win_opportunity(opportunity.id)
    print("✓ Opportunity WON!")
    print(f"  - Final stage: {opportunity.stage}")
    print(f"  - Close date: {opportunity.actual_close_date}")

    # ===== EXAMPLE 6: List and Search =====
    print("\n6. Listing and searching...")

    # List all partners
    partners = await partner_service.list_partners(is_customer=True)
    print(f"✓ Total customers: {partners.total}")
    for p in partners.partners:
        print(f"  - {p.name} ({p.id})")

    # List partner contacts
    contacts = await contact_service.get_partner_contacts(partner.id)
    print(f"\n✓ Contacts for {partner.name}: {contacts.total}")
    for c in contacts.contacts:
        print(f"  - {c.full_name} ({c.job_title})")

    # List opportunities
    opportunities = await opportunity_service.list_opportunities(stage="WON")
    print(f"\n✓ Won opportunities: {opportunities.total}")
    for o in opportunities.opportunities:
        print(f"  - {o.name}: {o.amount}")

    print("\n" + "=" * 60)
    print("CRM Module Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
