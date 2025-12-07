"""
Data Transfer Objects (DTOs) for CRM module.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

# Partner DTOs


class PartnerCreateDTO(BaseModel):
    """DTO for creating a partner."""

    name: str = Field(min_length=2, max_length=255)
    partner_type: str = Field(pattern="^(INDIVIDUAL|COMPANY)$")
    is_customer: bool = False
    is_supplier: bool = False
    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    tax_id: str | None = None
    company_registry: str | None = None
    industry: str | None = None
    employee_count: int | None = Field(None, ge=0)
    annual_revenue_amount: Decimal | None = None
    annual_revenue_currency: str | None = Field(None, pattern="^[A-Z]{3}$")
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


class PartnerUpdateDTO(BaseModel):
    """DTO for updating a partner."""

    name: str | None = Field(None, min_length=2, max_length=255)
    is_customer: bool | None = None
    is_supplier: bool | None = None
    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    tax_id: str | None = None
    company_registry: str | None = None
    industry: str | None = None
    employee_count: int | None = Field(None, ge=0)
    annual_revenue_amount: Decimal | None = None
    annual_revenue_currency: str | None = Field(None, pattern="^[A-Z]{3}$")
    notes: str | None = None
    tags: list[str] | None = None


class PartnerDTO(BaseModel):
    """DTO for partner representation."""

    id: str
    name: str
    partner_type: str
    is_customer: bool
    is_supplier: bool
    is_active: bool
    email: str | None
    phone: str | None
    website: str | None
    billing_address: dict | None
    shipping_address: dict | None
    tax_id: str | None
    company_registry: str | None
    industry: str | None
    employee_count: int | None
    annual_revenue: str | None
    notes: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


# Contact DTOs


class ContactCreateDTO(BaseModel):
    """DTO for creating a contact."""

    partner_id: str
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    is_primary: bool = False
    email: EmailStr | None = None
    phone: str | None = None
    mobile: str | None = None
    job_title: str | None = None
    department: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


class ContactUpdateDTO(BaseModel):
    """DTO for updating a contact."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    is_primary: bool | None = None
    email: EmailStr | None = None
    phone: str | None = None
    mobile: str | None = None
    job_title: str | None = None
    department: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


class ContactDTO(BaseModel):
    """DTO for contact representation."""

    id: str
    partner_id: str
    first_name: str
    last_name: str
    full_name: str
    is_primary: bool
    is_active: bool
    email: str | None
    phone: str | None
    mobile: str | None
    job_title: str | None
    department: str | None
    address: dict | None
    notes: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


# Lead DTOs


class LeadCreateDTO(BaseModel):
    """DTO for creating a lead."""

    name: str = Field(min_length=1, max_length=255)
    company: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    source: str | None = None
    score: int = Field(0, ge=0, le=100)
    interest_level: str | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


class LeadUpdateDTO(BaseModel):
    """DTO for updating a lead."""

    name: str | None = Field(None, min_length=1, max_length=255)
    company: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    source: str | None = None
    score: int | None = Field(None, ge=0, le=100)
    interest_level: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


class LeadDTO(BaseModel):
    """DTO for lead representation."""

    id: str
    name: str
    company: str | None
    status: str
    email: str | None
    phone: str | None
    source: str | None
    score: int
    interest_level: str | None
    converted_to_partner_id: str | None
    converted_at: datetime | None
    notes: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class LeadQualifyDTO(BaseModel):
    """DTO for qualifying a lead and converting to partner."""

    create_contact: bool = True


# Opportunity DTOs


class OpportunityCreateDTO(BaseModel):
    """DTO for creating an opportunity."""

    partner_id: str
    name: str = Field(min_length=1, max_length=255)
    amount: Decimal | None = None
    currency: str = Field("USD", pattern="^[A-Z]{3}$")
    probability: int = Field(0, ge=0, le=100)
    expected_close_date: date | None = None
    source: str | None = None
    campaign: str | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


class OpportunityUpdateDTO(BaseModel):
    """DTO for updating an opportunity."""

    name: str | None = Field(None, min_length=1, max_length=255)
    stage: str | None = Field(
        None,
        pattern="^(PROSPECTING|QUALIFICATION|PROPOSAL|NEGOTIATION|WON|LOST)$",
    )
    amount: Decimal | None = None
    currency: str | None = Field(None, pattern="^[A-Z]{3}$")
    probability: int | None = Field(None, ge=0, le=100)
    expected_close_date: date | None = None
    source: str | None = None
    campaign: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


class OpportunityDTO(BaseModel):
    """DTO for opportunity representation."""

    id: str
    partner_id: str
    name: str
    stage: str
    amount: str | None
    probability: int
    expected_value: str | None
    expected_close_date: date | None
    actual_close_date: date | None
    source: str | None
    campaign: str | None
    notes: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


# List/Query DTOs


class PartnerListDTO(BaseModel):
    """DTO for listing partners."""

    partners: list[PartnerDTO]
    total: int
    skip: int
    limit: int


class ContactListDTO(BaseModel):
    """DTO for listing contacts."""

    contacts: list[ContactDTO]
    total: int
    skip: int
    limit: int


class LeadListDTO(BaseModel):
    """DTO for listing leads."""

    leads: list[LeadDTO]
    total: int
    skip: int
    limit: int


class OpportunityListDTO(BaseModel):
    """DTO for listing opportunities."""

    opportunities: list[OpportunityDTO]
    total: int
    skip: int
    limit: int
