"""
Value objects for serp-common module.

Re-exports from serp-resources for convenience.
"""

from serp_resources import Address, Email, Money, PhoneNumber, TaxId

__all__ = [
    "Address",
    "Email",
    "PhoneNumber",
    "Money",
    "TaxId",
]
