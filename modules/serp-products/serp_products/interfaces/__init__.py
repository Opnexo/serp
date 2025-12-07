"""Interfaces layer exports."""

from serp_products.interfaces.api_routes import router
from serp_products.interfaces.permissions import (
    ADMIN_PERMISSIONS,
    USER_PERMISSIONS,
)

__all__ = ["router", "ADMIN_PERMISSIONS", "USER_PERMISSIONS"]
