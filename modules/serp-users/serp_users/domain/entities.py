"""Domain entities for users module."""

from dataclasses import dataclass, field
from datetime import datetime

from serp_core.domain.entity import AggregateRoot, Entity

from serp_users.domain.value_objects import Email


@dataclass
class User(AggregateRoot):
    """User aggregate root."""

    username: str
    email: Email
    password_hash: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    tenant_id: str | None = None
    avatar_url: str | None = None
    last_login: datetime | None = None
    metadata: dict = field(default_factory=dict)

    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False

    def add_role(self, role: str) -> None:
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: str) -> None:
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)

    def grant_permission(self, permission: str) -> None:
        """Grant a permission to the user."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def revoke_permission(self, permission: str) -> None:
        """Revoke a permission from the user."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return self.is_superuser or permission in self.permissions

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()


@dataclass
class Role(Entity):
    """Role entity for grouping permissions."""

    name: str
    description: str
    permissions: list[str] = field(default_factory=list)
    is_system: bool = False

    def add_permission(self, permission: str) -> None:
        """Add a permission to the role."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: str) -> None:
        """Remove a permission from the role."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission."""
        return permission in self.permissions


@dataclass
class Session(Entity):
    """User session entity."""

    user_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    is_active: bool = True

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    def revoke(self) -> None:
        """Revoke the session."""
        self.is_active = False
