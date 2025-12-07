"""
Role management for authorization
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Role:
    """
    Represents a role in the system.

    Roles group permissions together for easier management.

    Example:
        admin_role = Role(
            name="admin",
            display_name="Administrator",
            description="Full system access",
            permissions=[
                "users.create",
                "users.view",
                "users.edit",
                "users.delete",
                "customers.create",
                "customers.view",
                # ... etc
            ]
        )

        sales_role = Role(
            name="sales",
            display_name="Sales Representative",
            description="Can manage customers and orders",
            permissions=[
                "customers.view",
                "customers.create",
                "customers.edit",
                "orders.view",
                "orders.create",
            ]
        )
    """

    name: str
    display_name: str
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    is_system: bool = False  # System roles cannot be deleted

    def __str__(self) -> str:
        return self.name

    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission"""
        return permission in self.permissions

    def add_permission(self, permission: str) -> None:
        """Add a permission to the role"""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: str) -> None:
        """Remove a permission from the role"""
        if permission in self.permissions:
            self.permissions.remove(permission)
