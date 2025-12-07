"""
SERP Inventory Module

Warehouse management and stock tracking.
"""

from serp_inventory.config import InventorySettings
from serp_inventory.interfaces import router

MODULE_INFO = {
    "name": "inventory",
    "version": "0.1.0",
    "description": "Warehouse management and stock tracking",
    "settings_class": InventorySettings,
}

__all__ = ["MODULE_INFO", "router"]
__version__ = "0.1.0"
