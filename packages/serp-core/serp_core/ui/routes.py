"""
Route configuration types
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RouteConfig:
    """
    Represents a route configuration for module UI.

    Example:
        customer_routes = RouteConfig(
            path="/customers",
            component="CustomerList",
            permission="customers.view",
            title="Customers"
        )
    """

    path: str
    component: str
    permission: Optional[str] = None
    title: Optional[str] = None
    icon: Optional[str] = None
