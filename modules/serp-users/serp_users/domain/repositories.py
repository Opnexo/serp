"""Repository interfaces for users module."""

from abc import abstractmethod

from serp_core.domain.repository import Repository

from serp_users.domain.entities import Role, Session, User


class IUserRepository(Repository[User]):
    """User repository interface."""

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """Find user by email."""
        pass

    @abstractmethod
    async def find_by_tenant(self, tenant_id: str) -> list[User]:
        """Find all users in a tenant."""
        pass

    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """Check if username exists."""
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email exists."""
        pass


class IRoleRepository(Repository[Role]):
    """Role repository interface."""

    @abstractmethod
    async def find_by_name(self, name: str) -> Role | None:
        """Find role by name."""
        pass

    @abstractmethod
    async def find_system_roles(self) -> list[Role]:
        """Find all system roles."""
        pass


class ISessionRepository(Repository[Session]):
    """Session repository interface."""

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[Session]:
        """Find all sessions for a user."""
        pass

    @abstractmethod
    async def find_by_access_token(self, token: str) -> Session | None:
        """Find session by access token."""
        pass

    @abstractmethod
    async def find_by_refresh_token(self, token: str) -> Session | None:
        """Find session by refresh token."""
        pass

    @abstractmethod
    async def revoke_user_sessions(self, user_id: str) -> None:
        """Revoke all sessions for a user."""
        pass
