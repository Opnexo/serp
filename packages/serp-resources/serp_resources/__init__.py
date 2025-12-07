"""
SERP Resources - Shared value objects and utilities for SERP modules.
"""

from serp_resources.value_objects.address import Address
from serp_resources.value_objects.email import Email
from serp_resources.value_objects.money import Money
from serp_resources.value_objects.phone import PhoneNumber
from serp_resources.value_objects.tax_id import TaxId

__version__ = "0.1.0"

__all__ = [
    "Address",
    "Email",
    "Money",
    "PhoneNumber",
    "TaxId",
]
