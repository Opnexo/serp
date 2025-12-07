"""
SERP Products Module

Product catalog management with multi-UoM and dynamic attributes.
"""

from serp_products.config import ProductsSettings
from serp_products.interfaces import router

MODULE_INFO = {
    "name": "products",
    "version": "0.1.0",
    "description": "Product catalog management",
    "settings_class": ProductsSettings,
}

__version__ = "0.1.0"
__all__ = ["router", "MODULE_INFO", "ProductsSettings"]
