"""
Authentication context management
"""

from contextvars import ContextVar
from typing import Any, Dict, Optional
from uuid import UUID

# Context variable to store current user across async calls
_current_user: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "current_user", default=None
)


class AuthContext:
    """
    Authentication context for the current request.

    Stores information about the authenticated user.

    Example:
        # In middleware:
        user_data = {
            "id": user.id,
            "email": user.email,
            "permissions": ["users.view", "users.create"],
            "roles": ["admin"]
        }
        auth_context = AuthContext(user_data)
        auth_context.set()

        # In application code:
        user = get_current_user()
        user_id = user["id"]
        has_perm = "users.create" in user.get("permissions", [])
    """

    def __init__(self, user: Dict[str, Any]) -> None:
        self.user = user

    def set(self) -> None:
        """Set the current user in context"""
        _current_user.set(self.user)

    @staticmethod
    def clear() -> None:
        """Clear the current user from context"""
        _current_user.set(None)

    @property
    def user_id(self) -> Optional[UUID]:
        """Get the current user ID"""
        return self.user.get("id") if self.user else None

    @property
    def is_authenticated(self) -> bool:
        """Check if a user is authenticated"""
        return self.user is not None

    def has_permission(self, permission: str) -> bool:
        """Check if current user has a permission"""
        if not self.user:
            return False
        user_permissions = self.user.get("permissions", [])
        return permission in user_permissions

    def has_any_permission(self, *permissions: str) -> bool:
        """Check if current user has any of the given permissions"""
        if not self.user:
            return False
        user_permissions = set(self.user.get("permissions", []))
        return bool(user_permissions.intersection(permissions))

    def has_all_permissions(self, *permissions: str) -> bool:
        """Check if current user has all of the given permissions"""
        if not self.user:
            return False
        user_permissions = set(self.user.get("permissions", []))
        return set(permissions).issubset(user_permissions)


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from context.

    Returns:
        User dictionary if authenticated, None otherwise
    """
    return _current_user.get()


def get_auth_context() -> AuthContext:
    """
    Get the current authentication context.

    Returns:
        AuthContext instance with current user data
    """
    user = get_current_user()
    return AuthContext(user) if user else AuthContext({})
