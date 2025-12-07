"""
SERP Logistics Module

Fulfillment, picking, packing, and shipping management.
"""

from serp_logistics.config import LogisticsSettings

MODULE_INFO = {
    "name": "logistics",
    "version": "0.1.0",
    "description": "Fulfillment, picking, packing, and shipping management",
    "settings_class": LogisticsSettings,
}

__version__ = "0.1.0"
