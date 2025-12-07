"""
Domain entities for CRM module.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from serp_core.domain.aggregate import AggregateRoot

from serp_crm.domain.value_objects import Address, Email, Money, PhoneNumber, TaxId


class PartnerType(str, Enum):
    """Type of partner entity."""

    INDIVIDUAL = "INDIVIDUAL"  # Person
    COMPANY = "COMPANY"  # Organization


class LeadStatus(str, Enum):
    """Status of a lead in the qualification process."""

    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    LOST = "LOST"


class OpportunityStage(str, Enum):
    """Stage of an opportunity in the sales pipeline."""

    PROSPECTING = "PROSPECTING"
    QUALIFICATION = "QUALIFICATION"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"


class ActivityType(str, Enum):
    """Type of activity/interaction."""

    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    NOTE = "NOTE"
    TASK = "TASK"


@dataclass
class Partner(AggregateRoot):
    """
    Partner aggregate root - Unified entity for customers, suppliers, etc.

    The Partner pattern allows a single entity to represent multiple roles:
    - Customer (is_customer=True)
    - Supplier (is_supplier=True)
    - Both (common in B2B)
    - Neither (potential partner, past partner, etc.)
    """

    name: str = ""
    partner_type: PartnerType = PartnerType.INDIVIDUAL
    is_customer: bool = False
    is_supplier: bool = False
    is_active: bool = True

    # Contact info
    email: Email | None = None
    phone: PhoneNumber | None = None
    website: str | None = None

    # Address
    billing_address: Address | None = None
    shipping_address: Address | None = None

    # Tax & Legal
    tax_id: TaxId | None = None
    company_registry: str | None = None

    # Business details
    industry: str | None = None
    employee_count: int | None = None
    annual_revenue: Money | None = None

    # Internal tracking
    notes: str | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name or len(self.name) < 2:
            raise ValueError("Partner name must be at least 2 characters")

    def activate(self) -> None:
        """Activate this partner."""
        if self.is_active:
            raise ValueError("Partner is already active")
        self.is_active = True
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """Deactivate this partner."""
        if not self.is_active:
            raise ValueError("Partner is already inactive")
        self.is_active = False
        self.updated_at = datetime.now()

    def mark_as_customer(self) -> None:
        """Mark this partner as a customer."""
        self.is_customer = True
        self.updated_at = datetime.now()

    def mark_as_supplier(self) -> None:
        """Mark this partner as a supplier."""
        self.is_supplier = True
        self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Add a tag to this partner."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this partner."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "partner_type": self.partner_type.value,
            "is_customer": self.is_customer,
            "is_supplier": self.is_supplier,
            "is_active": self.is_active,
            "email": str(self.email) if self.email else None,
            "phone": str(self.phone) if self.phone else None,
            "website": self.website,
            "billing_address": self.billing_address.to_dict()
            if self.billing_address
            else None,
            "shipping_address": self.shipping_address.to_dict()
            if self.shipping_address
            else None,
            "tax_id": str(self.tax_id) if self.tax_id else None,
            "company_registry": self.company_registry,
            "industry": self.industry,
            "employee_count": self.employee_count,
            "annual_revenue": str(self.annual_revenue) if self.annual_revenue else None,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Contact(AggregateRoot):
    """
    Contact aggregate root - Person associated with a Partner.

    Separate aggregate from Partner to allow independent lifecycle.
    References Partner via partner_id (cross-aggregate reference).
    """

    partner_id: str = ""  # Foreign key to Partner
    first_name: str = ""
    last_name: str = ""
    is_primary: bool = False  # Primary contact for the partner
    is_active: bool = True

    # Contact info
    email: Email | None = None
    phone: PhoneNumber | None = None
    mobile: PhoneNumber | None = None

    # Position
    job_title: str | None = None
    department: str | None = None

    # Address (if different from partner)
    address: Address | None = None

    # Internal tracking
    notes: str | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.first_name or not self.last_name:
            raise ValueError("First name and last name are required")

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}"

    def activate(self) -> None:
        """Activate this contact."""
        if self.is_active:
            raise ValueError("Contact is already active")
        self.is_active = True
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """Deactivate this contact."""
        if not self.is_active:
            raise ValueError("Contact is already inactive")
        self.is_active = False
        self.updated_at = datetime.now()

    def set_as_primary(self) -> None:
        """Set this contact as primary for the partner."""
        self.is_primary = True
        self.updated_at = datetime.now()

    def unset_as_primary(self) -> None:
        """Unset this contact as primary for the partner."""
        self.is_primary = False
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "partner_id": self.partner_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "is_primary": self.is_primary,
            "is_active": self.is_active,
            "email": str(self.email) if self.email else None,
            "phone": str(self.phone) if self.phone else None,
            "mobile": str(self.mobile) if self.mobile else None,
            "job_title": self.job_title,
            "department": self.department,
            "address": self.address.to_dict() if self.address else None,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Lead(AggregateRoot):
    """
    Lead aggregate root - Potential partner/customer.

    Leads are qualified and converted to Partners.
    Separate aggregate with its own lifecycle.
    """

    name: str = ""
    company: str | None = None
    status: LeadStatus = LeadStatus.NEW

    # Contact info
    email: Email | None = None
    phone: PhoneNumber | None = None

    # Qualification
    source: str | None = None  # Web, referral, event, etc.
    score: int = 0  # Lead scoring (0-100)
    interest_level: str | None = None  # High, Medium, Low

    # Conversion
    converted_to_partner_id: str | None = None
    converted_at: datetime | None = None

    # Internal tracking
    notes: str | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name:
            raise ValueError("Lead name is required")
        if not 0 <= self.score <= 100:
            raise ValueError("Lead score must be between 0 and 100")

    def contact(self) -> None:
        """Mark lead as contacted."""
        if self.status == LeadStatus.QUALIFIED:
            raise ValueError("Cannot contact a qualified lead")
        if self.status == LeadStatus.LOST:
            raise ValueError("Cannot contact a lost lead")
        self.status = LeadStatus.CONTACTED
        self.updated_at = datetime.now()

    def qualify(self) -> None:
        """Qualify the lead."""
        if self.status == LeadStatus.QUALIFIED:
            raise ValueError("Lead is already qualified")
        if self.status == LeadStatus.LOST:
            raise ValueError("Cannot qualify a lost lead")
        self.status = LeadStatus.QUALIFIED
        self.updated_at = datetime.now()

    def lose(self) -> None:
        """Mark lead as lost."""
        if self.status == LeadStatus.QUALIFIED:
            raise ValueError("Cannot lose a qualified lead")
        self.status = LeadStatus.LOST
        self.updated_at = datetime.now()

    def convert_to_partner(self, partner_id: str) -> None:
        """Convert lead to partner."""
        if self.status != LeadStatus.QUALIFIED:
            raise ValueError("Only qualified leads can be converted")
        if self.converted_to_partner_id:
            raise ValueError("Lead has already been converted")
        self.converted_to_partner_id = partner_id
        self.converted_at = datetime.now()
        self.updated_at = datetime.now()

    def update_score(self, score: int) -> None:
        """Update lead score."""
        if not 0 <= score <= 100:
            raise ValueError("Lead score must be between 0 and 100")
        self.score = score
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "company": self.company,
            "status": self.status.value,
            "email": str(self.email) if self.email else None,
            "phone": str(self.phone) if self.phone else None,
            "source": self.source,
            "score": self.score,
            "interest_level": self.interest_level,
            "converted_to_partner_id": self.converted_to_partner_id,
            "converted_at": self.converted_at.isoformat()
            if self.converted_at
            else None,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Opportunity(AggregateRoot):
    """
    Opportunity aggregate root - Sales deal in the pipeline.

    References Partner (customer) via partner_id.
    Separate aggregate with its own lifecycle.
    """

    partner_id: str = ""  # Foreign key to Partner (customer)
    name: str = ""
    stage: OpportunityStage = OpportunityStage.PROSPECTING

    # Financial
    amount: Money | None = None
    probability: int = 0  # Win probability (0-100%)

    # Timeline
    expected_close_date: date | None = None
    actual_close_date: date | None = None

    # Tracking
    source: str | None = None
    campaign: str | None = None

    # Internal tracking
    notes: str | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name:
            raise ValueError("Opportunity name is required")
        if not 0 <= self.probability <= 100:
            raise ValueError("Probability must be between 0 and 100")

    def move_to_stage(self, stage: OpportunityStage) -> None:
        """Move opportunity to a new stage."""
        if self.stage in (OpportunityStage.WON, OpportunityStage.LOST):
            raise ValueError("Cannot change stage of won/lost opportunity")
        self.stage = stage
        self.updated_at = datetime.now()

    def win(self) -> None:
        """Mark opportunity as won."""
        if self.stage == OpportunityStage.WON:
            raise ValueError("Opportunity is already won")
        if self.stage == OpportunityStage.LOST:
            raise ValueError("Cannot win a lost opportunity")
        self.stage = OpportunityStage.WON
        self.actual_close_date = date.today()
        self.probability = 100
        self.updated_at = datetime.now()

    def lose(self) -> None:
        """Mark opportunity as lost."""
        if self.stage == OpportunityStage.LOST:
            raise ValueError("Opportunity is already lost")
        if self.stage == OpportunityStage.WON:
            raise ValueError("Cannot lose a won opportunity")
        self.stage = OpportunityStage.LOST
        self.actual_close_date = date.today()
        self.probability = 0
        self.updated_at = datetime.now()

    def update_amount(self, amount: Money) -> None:
        """Update opportunity amount."""
        self.amount = amount
        self.updated_at = datetime.now()

    def update_probability(self, probability: int) -> None:
        """Update win probability."""
        if not 0 <= probability <= 100:
            raise ValueError("Probability must be between 0 and 100")
        self.probability = probability
        self.updated_at = datetime.now()

    @property
    def expected_value(self) -> Money | None:
        """Calculate expected value (amount * probability)."""
        if not self.amount:
            return None
        expected_amount = self.amount.amount * Decimal(self.probability) / Decimal(100)
        return Money(expected_amount, self.amount.currency)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "partner_id": self.partner_id,
            "name": self.name,
            "stage": self.stage.value,
            "amount": str(self.amount) if self.amount else None,
            "probability": self.probability,
            "expected_value": str(self.expected_value) if self.expected_value else None,
            "expected_close_date": self.expected_close_date.isoformat()
            if self.expected_close_date
            else None,
            "actual_close_date": self.actual_close_date.isoformat()
            if self.actual_close_date
            else None,
            "source": self.source,
            "campaign": self.campaign,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
