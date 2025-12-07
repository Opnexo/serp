"""
SERP Common Module

Shared entities, value objects, and UI components used across SERP modules.
"""

from serp_core.plugins.types import ModuleInfo

from serp_common.application.services import AddressService
from serp_common.application.dto import AddressDTO, AddressCreateDTO, AddressUpdateDTO
from serp_common.domain.entities import AddressEntity
from serp_common.domain.value_objects import Address, Email, PhoneNumber, Money, TaxId

__version__ = "0.1.0"

MODULE_INFO = ModuleInfo(
    name="common",
    version=__version__,
    display_name="Common Resources",
    description="Shared entities, value objects, and UI components",
    author="SERP Team",
    dependencies=["serp-core>=1.0.0", "serp-resources>=0.1.0"],
)

__all__ = [
    # Entities
    "AddressEntity",
    # Value Objects (re-exported from serp-resources)
    "Address",
    "Email",
    "PhoneNumber",
    "Money",
    "TaxId",
    # Services
    "AddressService",
    # DTOs
    "AddressDTO",
    "AddressCreateDTO",
    "AddressUpdateDTO",
    # Module info
    "MODULE_INFO",
]
