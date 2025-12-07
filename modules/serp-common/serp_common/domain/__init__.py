"""
Domain layer for serp-common module.
"""

from serp_common.domain.entities import AddressEntity
from serp_common.domain.value_objects import Address, Email, PhoneNumber, Money, TaxId
from serp_common.domain.repositories import IAddressRepository

__all__ = [
    "AddressEntity",
    "Address",
    "Email",
    "PhoneNumber",
    "Money",
    "TaxId",
    "IAddressRepository",
]
