"""
Domain events for CRM module.
"""

from dataclasses import dataclass
from datetime import datetime

from serp_core.domain.events import DomainEvent

# Partner Events


@dataclass
class PartnerCreated(DomainEvent):
    """Event raised when a partner is created."""

    partner_id: str
    name: str
    partner_type: str
    is_customer: bool
    is_supplier: bool
    occurred_at: datetime


@dataclass
class PartnerUpdated(DomainEvent):
    """Event raised when a partner is updated."""

    partner_id: str
    occurred_at: datetime


@dataclass
class PartnerActivated(DomainEvent):
    """Event raised when a partner is activated."""

    partner_id: str
    occurred_at: datetime


@dataclass
class PartnerDeactivated(DomainEvent):
    """Event raised when a partner is deactivated."""

    partner_id: str
    occurred_at: datetime


@dataclass
class PartnerDeleted(DomainEvent):
    """Event raised when a partner is deleted."""

    partner_id: str
    occurred_at: datetime


# Contact Events


@dataclass
class ContactCreated(DomainEvent):
    """Event raised when a contact is created."""

    contact_id: str
    partner_id: str
    full_name: str
    is_primary: bool
    occurred_at: datetime


@dataclass
class ContactUpdated(DomainEvent):
    """Event raised when a contact is updated."""

    contact_id: str
    partner_id: str
    occurred_at: datetime


@dataclass
class ContactSetAsPrimary(DomainEvent):
    """Event raised when a contact is set as primary."""

    contact_id: str
    partner_id: str
    occurred_at: datetime


@dataclass
class ContactDeleted(DomainEvent):
    """Event raised when a contact is deleted."""

    contact_id: str
    partner_id: str
    occurred_at: datetime


# Lead Events


@dataclass
class LeadCreated(DomainEvent):
    """Event raised when a lead is created."""

    lead_id: str
    name: str
    company: str | None
    occurred_at: datetime


@dataclass
class LeadContacted(DomainEvent):
    """Event raised when a lead is contacted."""

    lead_id: str
    occurred_at: datetime


@dataclass
class LeadQualified(DomainEvent):
    """Event raised when a lead is qualified."""

    lead_id: str
    occurred_at: datetime


@dataclass
class LeadLost(DomainEvent):
    """Event raised when a lead is lost."""

    lead_id: str
    occurred_at: datetime


@dataclass
class LeadConverted(DomainEvent):
    """Event raised when a lead is converted to a partner."""

    lead_id: str
    partner_id: str
    occurred_at: datetime


# Opportunity Events


@dataclass
class OpportunityCreated(DomainEvent):
    """Event raised when an opportunity is created."""

    opportunity_id: str
    partner_id: str
    name: str
    occurred_at: datetime


@dataclass
class OpportunityStageChanged(DomainEvent):
    """Event raised when an opportunity stage changes."""

    opportunity_id: str
    old_stage: str
    new_stage: str
    occurred_at: datetime


@dataclass
class OpportunityWon(DomainEvent):
    """Event raised when an opportunity is won."""

    opportunity_id: str
    partner_id: str
    amount: str | None
    occurred_at: datetime


@dataclass
class OpportunityLost(DomainEvent):
    """Event raised when an opportunity is lost."""

    opportunity_id: str
    partner_id: str
    occurred_at: datetime
