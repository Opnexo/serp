"""In-memory repository implementations for users module."""

from serp_users.domain.entities import Role, Session, User
from serp_users.domain.repositories import (
    IRoleRepository,
    ISessionRepository,
    IUserRepository,
)


class InMemoryUserRepository(IUserRepository):
    """In-memory implementation of user repository."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    async def save(self, entity: User) -> User:
        """Save user."""
        self._users[entity.id] = entity
        return entity

    async def find_by_id(self, entity_id: str) -> User | None:
        """Find user by ID."""
        return self._users.get(entity_id)

    async def find_all(self) -> list[User]:
        """Find all users."""
        return list(self._users.values())

    async def delete(self, entity_id: str) -> None:
        """Delete user."""
        if entity_id in self._users:
            del self._users[entity_id]

    async def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    async def find_by_email(self, email: str) -> User | None:
        """Find user by email."""
        for user in self._users.values():
            if str(user.email) == email:
                return user
        return None

    async def find_by_tenant(self, tenant_id: str) -> list[User]:
        """Find all users in a tenant."""
        return [u for u in self._users.values() if u.tenant_id == tenant_id]

    async def username_exists(self, username: str) -> bool:
        """Check if username exists."""
        return any(u.username == username for u in self._users.values())

    async def email_exists(self, email: str) -> bool:
        """Check if email exists."""
        return any(str(u.email) == email for u in self._users.values())


class InMemoryRoleRepository(IRoleRepository):
    """In-memory implementation of role repository."""

    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}

    async def save(self, entity: Role) -> Role:
        """Save role."""
        self._roles[entity.id] = entity
        return entity

    async def find_by_id(self, entity_id: str) -> Role | None:
        """Find role by ID."""
        return self._roles.get(entity_id)

    async def find_all(self) -> list[Role]:
        """Find all roles."""
        return list(self._roles.values())

    async def delete(self, entity_id: str) -> None:
        """Delete role."""
        if entity_id in self._roles:
            del self._roles[entity_id]

    async def find_by_name(self, name: str) -> Role | None:
        """Find role by name."""
        for role in self._roles.values():
            if role.name == name:
                return role
        return None

    async def find_system_roles(self) -> list[Role]:
        """Find all system roles."""
        return [r for r in self._roles.values() if r.is_system]


class InMemorySessionRepository(ISessionRepository):
    """In-memory implementation of session repository."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    async def save(self, entity: Session) -> Session:
        """Save session."""
        self._sessions[entity.id] = entity
        return entity

    async def find_by_id(self, entity_id: str) -> Session | None:
        """Find session by ID."""
        return self._sessions.get(entity_id)

    async def find_all(self) -> list[Session]:
        """Find all sessions."""
        return list(self._sessions.values())

    async def delete(self, entity_id: str) -> None:
        """Delete session."""
        if entity_id in self._sessions:
            del self._sessions[entity_id]

    async def find_by_user_id(self, user_id: str) -> list[Session]:
        """Find all sessions for a user."""
        return [s for s in self._sessions.values() if s.user_id == user_id]

    async def find_by_access_token(self, token: str) -> Session | None:
        """Find session by access token."""
        for session in self._sessions.values():
            if session.access_token == token:
                return session
        return None

    async def find_by_refresh_token(self, token: str) -> Session | None:
        """Find session by refresh token."""
        for session in self._sessions.values():
            if session.refresh_token == token:
                return session
        return None

    async def revoke_user_sessions(self, user_id: str) -> None:
        """Revoke all sessions for a user."""
        for session in self._sessions.values():
            if session.user_id == user_id:
                session.revoke()
