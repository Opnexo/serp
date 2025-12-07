"""Domain events for users module."""

from dataclasses import dataclass

from serp_core.domain.events import DomainEvent


@dataclass
class UserCreated(DomainEvent):
    """Event raised when a user is created."""

    user_id: str
    username: str
    email: str


@dataclass
class UserUpdated(DomainEvent):
    """Event raised when a user is updated."""

    user_id: str
    username: str
    fields_updated: list[str]


@dataclass
class UserDeleted(DomainEvent):
    """Event raised when a user is deleted."""

    user_id: str
    username: str


@dataclass
class UserActivated(DomainEvent):
    """Event raised when a user is activated."""

    user_id: str
    username: str


@dataclass
class UserDeactivated(DomainEvent):
    """Event raised when a user is deactivated."""

    user_id: str
    username: str


@dataclass
class UserLoggedIn(DomainEvent):
    """Event raised when a user logs in."""

    user_id: str
    username: str
    ip_address: str | None


@dataclass
class UserLoggedOut(DomainEvent):
    """Event raised when a user logs out."""

    user_id: str
    username: str


@dataclass
class PasswordChanged(DomainEvent):
    """Event raised when a user's password is changed."""

    user_id: str
    username: str


@dataclass
class RoleAssigned(DomainEvent):
    """Event raised when a role is assigned to a user."""

    user_id: str
    username: str
    role: str


@dataclass
class RoleRevoked(DomainEvent):
    """Event raised when a role is revoked from a user."""

    user_id: str
    username: str
    role: str


@dataclass
class PermissionGranted(DomainEvent):
    """Event raised when a permission is granted to a user."""

    user_id: str
    username: str
    permission: str


@dataclass
class PermissionRevoked(DomainEvent):
    """Event raised when a permission is revoked from a user."""

    user_id: str
    username: str
    permission: str
