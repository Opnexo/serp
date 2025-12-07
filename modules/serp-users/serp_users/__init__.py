"""
SERP Users Module

User management, authentication, and authorization.
"""

from serp_users.application.services import AuthService, UserService
from serp_users.config import UsersSettings
from serp_users.domain.entities import Role, User
from serp_users.domain.value_objects import Email, Password

__version__ = "0.1.0"

MODULE_INFO = {
    "module_id": "users",
    "module_name": "User Management",
    "version": __version__,
    "description": "User management, authentication, and authorization",
    "author": "SERP Team",
    "permissions": [
        "users:list",
        "users:read",
        "users:create",
        "users:update",
        "users:delete",
        "users:manage_roles",
        "users:manage_permissions",
    ],
}

__all__ = [
    "User",
    "Role",
    "Email",
    "Password",
    "UserService",
    "AuthService",
    "UsersSettings",
    "MODULE_INFO",
]
