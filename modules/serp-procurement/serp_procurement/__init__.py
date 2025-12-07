"""
SERP Procurement Module

Purchase order management and supplier procurement.
"""

from serp_procurement.config import ProcurementSettings
from serp_procurement.interfaces import router

MODULE_INFO = {
    "name": "procurement",
    "version": "0.1.0",
    "description": "Purchase order and supplier procurement management",
    "settings_class": ProcurementSettings,
}

__version__ = "0.1.0"
__all__ = ["router", "MODULE_INFO", "ProcurementSettings"]
