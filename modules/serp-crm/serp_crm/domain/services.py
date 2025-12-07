"""
Domain services for CRM module.
"""

from serp_crm.domain.entities import Contact, Lead, Partner
from serp_crm.domain.repositories import IContactRepository, IPartnerRepository
from serp_crm.domain.value_objects import Email


class LeadConversionService:
    """
    Domain service for converting leads to partners.

    This is a domain service because it orchestrates multiple aggregates
    (Lead and Partner) and contains complex business logic.
    """

    def __init__(
        self,
        partner_repository: IPartnerRepository,
        contact_repository: IContactRepository,
    ):
        self.partner_repository = partner_repository
        self.contact_repository = contact_repository

    async def convert_lead_to_partner(
        self,
        lead: Lead,
        create_contact: bool = True,
    ) -> tuple[Partner, Contact | None]:
        """
        Convert a qualified lead to a partner.

        Args:
            lead: The qualified lead to convert
            create_contact: Whether to create a contact from the lead

        Returns:
            Tuple of (Partner, Contact or None)

        Raises:
            ValueError: If lead is not qualified or already converted
        """
        # Ensure lead is qualified
        if lead.status.value != "QUALIFIED":
            raise ValueError("Only qualified leads can be converted to partners")

        if lead.converted_to_partner_id:
            raise ValueError("Lead has already been converted")

        # Create partner from lead
        partner = Partner(
            name=lead.company or lead.name,
            partner_type="COMPANY" if lead.company else "INDIVIDUAL",
            is_customer=True,
            email=lead.email,
            phone=lead.phone,
            notes=lead.notes,
            tags=lead.tags,
        )

        # Save partner
        partner = await self.partner_repository.save(partner)

        # Update lead
        lead.convert_to_partner(partner.id)

        # Create contact if requested
        contact = None
        if create_contact and lead.email:
            # Extract first/last name from lead name
            name_parts = lead.name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            contact = Contact(
                partner_id=partner.id,
                first_name=first_name,
                last_name=last_name,
                email=lead.email,
                phone=lead.phone,
                is_primary=True,
                notes=f"Converted from lead: {lead.id}",
            )

            contact = await self.contact_repository.save(contact)

        return partner, contact


class PartnerMergeService:
    """
    Domain service for merging duplicate partners.

    This is a domain service because it involves complex business logic
    across multiple entities.
    """

    def __init__(
        self,
        partner_repository: IPartnerRepository,
        contact_repository: IContactRepository,
    ):
        self.partner_repository = partner_repository
        self.contact_repository = contact_repository

    async def merge_partners(
        self,
        primary_partner: Partner,
        duplicate_partner: Partner,
    ) -> Partner:
        """
        Merge a duplicate partner into the primary partner.

        Args:
            primary_partner: The partner to keep
            duplicate_partner: The partner to merge and delete

        Returns:
            The updated primary partner

        Raises:
            ValueError: If partners are the same
        """
        if primary_partner.id == duplicate_partner.id:
            raise ValueError("Cannot merge a partner with itself")

        # Merge data (keep non-empty fields from duplicate)
        if not primary_partner.email and duplicate_partner.email:
            primary_partner.email = duplicate_partner.email

        if not primary_partner.phone and duplicate_partner.phone:
            primary_partner.phone = duplicate_partner.phone

        if not primary_partner.billing_address and duplicate_partner.billing_address:
            primary_partner.billing_address = duplicate_partner.billing_address

        # Merge flags (OR operation)
        primary_partner.is_customer = (
            primary_partner.is_customer or duplicate_partner.is_customer
        )
        primary_partner.is_supplier = (
            primary_partner.is_supplier or duplicate_partner.is_supplier
        )

        # Merge tags
        for tag in duplicate_partner.tags:
            if tag not in primary_partner.tags:
                primary_partner.tags.append(tag)

        # Append notes
        if duplicate_partner.notes:
            if primary_partner.notes:
                primary_partner.notes += f"\n\n--- Merged from {duplicate_partner.name} ---\n{duplicate_partner.notes}"
            else:
                primary_partner.notes = duplicate_partner.notes

        # Move contacts from duplicate to primary
        duplicate_contacts = await self.contact_repository.get_by_partner_id(
            duplicate_partner.id
        )

        for contact in duplicate_contacts:
            contact.partner_id = primary_partner.id
            await self.contact_repository.save(contact)

        # Save primary partner
        primary_partner = await self.partner_repository.save(primary_partner)

        # Delete duplicate partner
        await self.partner_repository.delete(duplicate_partner.id)

        return primary_partner


class ContactDeduplicationService:
    """Domain service for finding and managing duplicate contacts."""

    def __init__(self, contact_repository: IContactRepository):
        self.contact_repository = contact_repository

    async def find_duplicate_contacts(
        self,
        partner_id: str,
        email: Email | None = None,
    ) -> list[Contact]:
        """
        Find potential duplicate contacts for a partner.

        Args:
            partner_id: The partner ID to search within
            email: Optional email to check for duplicates

        Returns:
            List of potential duplicate contacts
        """
        contacts = await self.contact_repository.get_by_partner_id(partner_id)

        if not email:
            return []

        # Find contacts with matching email
        duplicates = [
            contact for contact in contacts if contact.email and contact.email == email
        ]

        return duplicates
