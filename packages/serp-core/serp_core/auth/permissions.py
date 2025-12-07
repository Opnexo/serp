"""
Permission system for authorization
"""

from dataclasses import dataclass
from functools import wraps
from typing import Callable, List, Optional

from serp_core.exceptions.auth import PermissionDeniedError


@dataclass(frozen=True)
class Permission:
    """
    Represents a permission in the system.

    Permissions use dot notation: "module.resource.action"
    Examples:
        - "users.create"
        - "customers.view"
        - "orders.delete"
        - "reports.sales.export"

    Example:
        # Define permissions
        VIEW_CUSTOMERS = Permission(
            code="customers.view",
            name="View Customers",
            description="Can view customer list and details"
        )

        CREATE_ORDER = Permission(
            code="orders.create",
            name="Create Orders",
            description="Can create new orders"
        )
    """

    code: str
    name: str
    description: str = ""

    def __str__(self) -> str:
        return self.code


def require_permission(*permissions: str) -> Callable:
    """
    Decorator to require one or more permissions.

    Args:
        *permissions: Permission codes required to access the function

    Raises:
        PermissionDeniedError: If user doesn't have required permissions

    Example:
        @require_permission("customers.create")
        async def create_customer(data: dict):
            # Only users with "customers.create" permission can call this
            pass

        @require_permission("orders.view", "orders.approve")
        async def approve_order(order_id: UUID):
            # Requires BOTH permissions
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from serp_core.auth.context import get_current_user

            user = get_current_user()
            if user is None:
                raise PermissionDeniedError("Authentication required")

            user_permissions = set(user.get("permissions", []))
            required_permissions = set(permissions)

            if not required_permissions.issubset(user_permissions):
                missing = required_permissions - user_permissions
                raise PermissionDeniedError(
                    f"Missing permissions: {', '.join(missing)}"
                )

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            from serp_core.auth.context import get_current_user

            user = get_current_user()
            if user is None:
                raise PermissionDeniedError("Authentication required")

            user_permissions = set(user.get("permissions", []))
            required_permissions = set(permissions)

            if not required_permissions.issubset(user_permissions):
                missing = required_permissions - user_permissions
                raise PermissionDeniedError(
                    f"Missing permissions: {', '.join(missing)}"
                )

            return func(*args, **kwargs)

        # Return appropriate wrapper based on whether function is async
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class PermissionRegistry:
    """
    Registry for all permissions in the system.

    Modules register their permissions on startup.
    """

    def __init__(self) -> None:
        self._permissions: dict[str, Permission] = {}

    def register(self, permission: Permission) -> None:
        """Register a permission"""
        self._permissions[permission.code] = permission

    def get(self, code: str) -> Optional[Permission]:
        """Get a permission by code"""
        return self._permissions.get(code)

    def all(self) -> List[Permission]:
        """Get all registered permissions"""
        return list(self._permissions.values())

    def filter_by_module(self, module_name: str) -> List[Permission]:
        """Get all permissions for a module"""
        return [p for p in self._permissions.values() if p.code.startswith(module_name)]


# Global permission registry
_permission_registry = PermissionRegistry()


def get_permission_registry() -> PermissionRegistry:
    """Get the global permission registry"""
    return _permission_registry
