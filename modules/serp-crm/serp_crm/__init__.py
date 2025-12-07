"""
SERP CRM Module

Customer Relationship Management with Partner pattern.
"""

from serp_core.plugins.types import ModuleInfo

from serp_crm.application.services import (
    ContactService,
    LeadService,
    OpportunityService,
    PartnerService,
)
from serp_crm.domain.entities import Contact, Lead, Opportunity, Partner
from serp_crm.domain.value_objects import Address, Email, PhoneNumber

__version__ = "0.1.0"

MODULE_INFO = ModuleInfo(
    name="crm",
    version=__version__,
    display_name="Customer Relationship Management",
    description="CRM with Partner pattern for customers, suppliers, and contacts",
    author="SERP Team",
    dependencies=["serp-core>=1.0.0", "serp-resources>=0.1.0"],
)

__all__ = [
    "Partner",
    "Contact",
    "Lead",
    "Opportunity",
    "Email",
    "PhoneNumber",
    "Address",
    "PartnerService",
    "ContactService",
    "LeadService",
    "OpportunityService",
    "MODULE_INFO",
]
