"""
Value Objects for CRM domain.

Re-exports common value objects from serp-resources for convenience.
Module-specific value objects can be added here.
"""

# Re-export common value objects from serp-resources
from serp_resources import Address, Email, Money, PhoneNumber, TaxId

__all__ = [
    "Address",
    "Email",
    "Money",
    "PhoneNumber",
    "TaxId",
]
