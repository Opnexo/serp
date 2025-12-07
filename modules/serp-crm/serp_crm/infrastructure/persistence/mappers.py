"""
Mappers for converting between domain entities and SQLAlchemy models.
"""

from decimal import Decimal

from serp_crm.domain.entities import Contact, Lead, Opportunity, Partner
from serp_crm.domain.value_objects import Address, Email, Money, PhoneNumber, TaxId
from serp_crm.infrastructure.persistence.models import (
    ContactModel,
    LeadModel,
    OpportunityModel,
    PartnerModel,
)


class PartnerMapper:
    """Mapper for Partner entity <-> PartnerModel."""

    @staticmethod
    def to_model(entity: Partner) -> PartnerModel:
        """Convert Partner entity to PartnerModel."""
        return PartnerModel(
            id=entity.id,
            name=entity.name,
            partner_type=entity.partner_type,
            is_customer=entity.is_customer,
            is_supplier=entity.is_supplier,
            is_active=entity.is_active,
            email=str(entity.email) if entity.email else None,
            phone=str(entity.phone) if entity.phone else None,
            website=entity.website,
            billing_address=entity.billing_address.to_dict()
            if entity.billing_address
            else None,
            shipping_address=entity.shipping_address.to_dict()
            if entity.shipping_address
            else None,
            tax_id_value=entity.tax_id.value if entity.tax_id else None,
            tax_id_country=entity.tax_id.country if entity.tax_id else None,
            company_registry=entity.company_registry,
            industry=entity.industry,
            employee_count=entity.employee_count,
            annual_revenue_amount=entity.annual_revenue.amount
            if entity.annual_revenue
            else None,
            annual_revenue_currency=entity.annual_revenue.currency
            if entity.annual_revenue
            else None,
            notes=entity.notes,
            tags=entity.tags,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: PartnerModel) -> Partner:
        """Convert PartnerModel to Partner entity."""
        return Partner(
            id=model.id,
            name=model.name,
            partner_type=model.partner_type,
            is_customer=model.is_customer,
            is_supplier=model.is_supplier,
            is_active=model.is_active,
            email=Email(model.email) if model.email else None,
            phone=PhoneNumber(model.phone) if model.phone else None,
            website=model.website,
            billing_address=Address.from_dict(model.billing_address)
            if model.billing_address
            else None,
            shipping_address=Address.from_dict(model.shipping_address)
            if model.shipping_address
            else None,
            tax_id=TaxId(model.tax_id_value, model.tax_id_country)
            if model.tax_id_value and model.tax_id_country
            else None,
            company_registry=model.company_registry,
            industry=model.industry,
            employee_count=model.employee_count,
            annual_revenue=Money(
                Decimal(str(model.annual_revenue_amount)),
                model.annual_revenue_currency,
            )
            if model.annual_revenue_amount and model.annual_revenue_currency
            else None,
            notes=model.notes,
            tags=list(model.tags) if model.tags else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def update_model(model: PartnerModel, entity: Partner) -> PartnerModel:
        """Update PartnerModel from Partner entity."""
        model.name = entity.name
        model.partner_type = entity.partner_type
        model.is_customer = entity.is_customer
        model.is_supplier = entity.is_supplier
        model.is_active = entity.is_active
        model.email = str(entity.email) if entity.email else None
        model.phone = str(entity.phone) if entity.phone else None
        model.website = entity.website
        model.billing_address = (
            entity.billing_address.to_dict() if entity.billing_address else None
        )
        model.shipping_address = (
            entity.shipping_address.to_dict() if entity.shipping_address else None
        )
        model.tax_id_value = entity.tax_id.value if entity.tax_id else None
        model.tax_id_country = entity.tax_id.country if entity.tax_id else None
        model.company_registry = entity.company_registry
        model.industry = entity.industry
        model.employee_count = entity.employee_count
        model.annual_revenue_amount = (
            entity.annual_revenue.amount if entity.annual_revenue else None
        )
        model.annual_revenue_currency = (
            entity.annual_revenue.currency if entity.annual_revenue else None
        )
        model.notes = entity.notes
        model.tags = entity.tags
        model.updated_at = entity.updated_at
        return model


class ContactMapper:
    """Mapper for Contact entity <-> ContactModel."""

    @staticmethod
    def to_model(entity: Contact) -> ContactModel:
        """Convert Contact entity to ContactModel."""
        return ContactModel(
            id=entity.id,
            partner_id=entity.partner_id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_primary=entity.is_primary,
            is_active=entity.is_active,
            email=str(entity.email) if entity.email else None,
            phone=str(entity.phone) if entity.phone else None,
            mobile=str(entity.mobile) if entity.mobile else None,
            job_title=entity.job_title,
            department=entity.department,
            address=entity.address.to_dict() if entity.address else None,
            notes=entity.notes,
            tags=entity.tags,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: ContactModel) -> Contact:
        """Convert ContactModel to Contact entity."""
        return Contact(
            id=model.id,
            partner_id=model.partner_id,
            first_name=model.first_name,
            last_name=model.last_name,
            is_primary=model.is_primary,
            is_active=model.is_active,
            email=Email(model.email) if model.email else None,
            phone=PhoneNumber(model.phone) if model.phone else None,
            mobile=PhoneNumber(model.mobile) if model.mobile else None,
            job_title=model.job_title,
            department=model.department,
            address=Address.from_dict(model.address) if model.address else None,
            notes=model.notes,
            tags=list(model.tags) if model.tags else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def update_model(model: ContactModel, entity: Contact) -> ContactModel:
        """Update ContactModel from Contact entity."""
        model.partner_id = entity.partner_id
        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.is_primary = entity.is_primary
        model.is_active = entity.is_active
        model.email = str(entity.email) if entity.email else None
        model.phone = str(entity.phone) if entity.phone else None
        model.mobile = str(entity.mobile) if entity.mobile else None
        model.job_title = entity.job_title
        model.department = entity.department
        model.address = entity.address.to_dict() if entity.address else None
        model.notes = entity.notes
        model.tags = entity.tags
        model.updated_at = entity.updated_at
        return model


class LeadMapper:
    """Mapper for Lead entity <-> LeadModel."""

    @staticmethod
    def to_model(entity: Lead) -> LeadModel:
        """Convert Lead entity to LeadModel."""
        return LeadModel(
            id=entity.id,
            name=entity.name,
            company=entity.company,
            status=entity.status,
            email=str(entity.email) if entity.email else None,
            phone=str(entity.phone) if entity.phone else None,
            source=entity.source,
            score=entity.score,
            interest_level=entity.interest_level,
            converted_to_partner_id=entity.converted_to_partner_id,
            converted_at=entity.converted_at,
            notes=entity.notes,
            tags=entity.tags,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: LeadModel) -> Lead:
        """Convert LeadModel to Lead entity."""
        return Lead(
            id=model.id,
            name=model.name,
            company=model.company,
            status=model.status,
            email=Email(model.email) if model.email else None,
            phone=PhoneNumber(model.phone) if model.phone else None,
            source=model.source,
            score=model.score,
            interest_level=model.interest_level,
            converted_to_partner_id=model.converted_to_partner_id,
            converted_at=model.converted_at,
            notes=model.notes,
            tags=list(model.tags) if model.tags else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def update_model(model: LeadModel, entity: Lead) -> LeadModel:
        """Update LeadModel from Lead entity."""
        model.name = entity.name
        model.company = entity.company
        model.status = entity.status
        model.email = str(entity.email) if entity.email else None
        model.phone = str(entity.phone) if entity.phone else None
        model.source = entity.source
        model.score = entity.score
        model.interest_level = entity.interest_level
        model.converted_to_partner_id = entity.converted_to_partner_id
        model.converted_at = entity.converted_at
        model.notes = entity.notes
        model.tags = entity.tags
        model.updated_at = entity.updated_at
        return model


class OpportunityMapper:
    """Mapper for Opportunity entity <-> OpportunityModel."""

    @staticmethod
    def to_model(entity: Opportunity) -> OpportunityModel:
        """Convert Opportunity entity to OpportunityModel."""
        return OpportunityModel(
            id=entity.id,
            partner_id=entity.partner_id,
            name=entity.name,
            stage=entity.stage,
            amount=entity.amount.amount if entity.amount else None,
            currency=entity.amount.currency if entity.amount else None,
            probability=entity.probability,
            expected_close_date=entity.expected_close_date,
            actual_close_date=entity.actual_close_date,
            source=entity.source,
            campaign=entity.campaign,
            notes=entity.notes,
            tags=entity.tags,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: OpportunityModel) -> Opportunity:
        """Convert OpportunityModel to Opportunity entity."""
        return Opportunity(
            id=model.id,
            partner_id=model.partner_id,
            name=model.name,
            stage=model.stage,
            amount=Money(Decimal(str(model.amount)), model.currency)
            if model.amount and model.currency
            else None,
            probability=model.probability,
            expected_close_date=model.expected_close_date,
            actual_close_date=model.actual_close_date,
            source=model.source,
            campaign=model.campaign,
            notes=model.notes,
            tags=list(model.tags) if model.tags else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def update_model(model: OpportunityModel, entity: Opportunity) -> OpportunityModel:
        """Update OpportunityModel from Opportunity entity."""
        model.partner_id = entity.partner_id
        model.name = entity.name
        model.stage = entity.stage
        model.amount = entity.amount.amount if entity.amount else None
        model.currency = entity.amount.currency if entity.amount else None
        model.probability = entity.probability
        model.expected_close_date = entity.expected_close_date
        model.actual_close_date = entity.actual_close_date
        model.source = entity.source
        model.campaign = entity.campaign
        model.notes = entity.notes
        model.tags = entity.tags
        model.updated_at = entity.updated_at
        return model
