"""
SERP Sales Module

Sales order management with quotes and order fulfillment.
"""

from serp_sales.config import SalesSettings

MODULE_INFO = {
    "name": "sales",
    "version": "0.1.0",
    "description": "Sales order management",
    "settings_class": SalesSettings,
}

__version__ = "0.1.0"
