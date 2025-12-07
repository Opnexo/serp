"""Application services for users module."""

from datetime import datetime, timedelta

from jose import JWTError, jwt
from serp_core.exceptions.application import (
    NotFoundError,
)
from serp_core.exceptions.application import (
    ValidationError as AppValidationError,
)
from serp_core.exceptions.auth import AuthenticationError

from serp_users.application.dto import (
    LoginDTO,
    PasswordChangeDTO,
    TokenDTO,
    UserCreateDTO,
    UserDTO,
    UserUpdateDTO,
)
from serp_users.config import UsersSettings
from serp_users.domain.entities import Session, User
from serp_users.domain.events import (
    PasswordChanged,
    UserCreated,
    UserDeleted,
    UserLoggedIn,
    UserLoggedOut,
    UserUpdated,
)
from serp_users.domain.repositories import (
    ISessionRepository,
    IUserRepository,
)
from serp_users.domain.services import PasswordHasher
from serp_users.domain.value_objects import Email, Password, Username


class UserService:
    """Application service for user management."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._users = user_repository
        self._password_hasher = password_hasher

    async def create_user(self, data: UserCreateDTO) -> UserDTO:
        """Create a new user."""
        # Validate uniqueness
        if await self._users.username_exists(data.username):
            raise AppValidationError(f"Username '{data.username}' already exists")

        if await self._users.email_exists(data.email):
            raise AppValidationError(f"Email '{data.email}' already exists")

        # Create value objects
        email = Email(data.email)
        password = Password(data.password)
        username = Username(data.username)

        # Hash password
        password_hash = self._password_hasher.hash(password.value)

        # Create user entity
        user = User(
            id=self._generate_id(),
            username=username.value,
            email=email,
            password_hash=password_hash,
            full_name=data.full_name,
            is_active=data.is_active,
            is_superuser=data.is_superuser,
            tenant_id=data.tenant_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Raise domain event
        user.add_domain_event(
            UserCreated(
                user_id=user.id,
                username=user.username,
                email=str(user.email),
            )
        )

        # Save
        await self._users.save(user)

        return self._to_dto(user)

    async def get_user(self, user_id: str) -> UserDTO:
        """Get user by ID."""
        user = await self._users.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID '{user_id}' not found")
        return self._to_dto(user)

    async def get_user_by_username(self, username: str) -> UserDTO:
        """Get user by username."""
        user = await self._users.find_by_username(username)
        if not user:
            raise NotFoundError(f"User '{username}' not found")
        return self._to_dto(user)

    async def update_user(self, user_id: str, data: UserUpdateDTO) -> UserDTO:
        """Update user."""
        user = await self._users.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID '{user_id}' not found")

        fields_updated = []

        if data.email:
            # Validate email uniqueness
            existing = await self._users.find_by_email(data.email)
            if existing and existing.id != user_id:
                raise AppValidationError(f"Email '{data.email}' already exists")
            user.email = Email(data.email)
            fields_updated.append("email")

        if data.full_name:
            user.full_name = data.full_name
            fields_updated.append("full_name")

        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url
            fields_updated.append("avatar_url")

        if data.is_active is not None:
            user.is_active = data.is_active
            fields_updated.append("is_active")

        user.updated_at = datetime.utcnow()

        # Raise domain event
        user.add_domain_event(
            UserUpdated(
                user_id=user.id,
                username=user.username,
                fields_updated=fields_updated,
            )
        )

        await self._users.save(user)
        return self._to_dto(user)

    async def delete_user(self, user_id: str) -> None:
        """Delete user."""
        user = await self._users.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID '{user_id}' not found")

        user.add_domain_event(
            UserDeleted(
                user_id=user.id,
                username=user.username,
            )
        )

        await self._users.delete(user_id)

    async def change_password(self, user_id: str, data: PasswordChangeDTO) -> None:
        """Change user password."""
        user = await self._users.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID '{user_id}' not found")

        # Verify current password
        if not self._password_hasher.verify(data.current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")

        # Validate and hash new password
        new_password = Password(data.new_password)
        user.password_hash = self._password_hasher.hash(new_password.value)
        user.updated_at = datetime.utcnow()

        user.add_domain_event(
            PasswordChanged(
                user_id=user.id,
                username=user.username,
            )
        )

        await self._users.save(user)

    def _to_dto(self, user: User) -> UserDTO:
        """Convert user entity to DTO."""
        return UserDTO(
            id=user.id,
            username=user.username,
            email=str(user.email),
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            roles=user.roles,
            permissions=user.permissions,
            tenant_id=user.tenant_id,
            avatar_url=user.avatar_url,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _generate_id(self) -> str:
        """Generate unique ID."""
        from uuid import uuid4

        return str(uuid4())


class AuthService:
    """Application service for authentication."""

    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: ISessionRepository,
        password_hasher: PasswordHasher,
        settings: UsersSettings,
    ) -> None:
        self._users = user_repository
        self._sessions = session_repository
        self._password_hasher = password_hasher
        self._settings = settings

    async def login(self, data: LoginDTO, ip_address: str | None = None) -> TokenDTO:
        """Authenticate user and create session."""
        # Find user
        user = await self._users.find_by_username(data.username)
        if not user:
            raise AuthenticationError("Invalid username or password")

        # Verify password
        if not self._password_hasher.verify(data.password, user.password_hash):
            raise AuthenticationError("Invalid username or password")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        # Update last login
        user.update_last_login()
        await self._users.save(user)

        # Create tokens
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        # Create session
        session = Session(
            id=self._generate_id(),
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow()
            + timedelta(days=self._settings.refresh_token_expire_days),
            ip_address=ip_address,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await self._sessions.save(session)

        # Raise domain event
        user.add_domain_event(
            UserLoggedIn(
                user_id=user.id,
                username=user.username,
                ip_address=ip_address,
            )
        )

        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    async def logout(self, access_token: str) -> None:
        """Logout user and revoke session."""
        session = await self._sessions.find_by_access_token(access_token)
        if session:
            session.revoke()
            await self._sessions.save(session)

            user = await self._users.find_by_id(session.user_id)
            if user:
                user.add_domain_event(
                    UserLoggedOut(
                        user_id=user.id,
                        username=user.username,
                    )
                )

    async def refresh_token(self, refresh_token: str) -> TokenDTO:
        """Refresh access token."""
        # Find session
        session = await self._sessions.find_by_refresh_token(refresh_token)
        if not session or not session.is_active:
            raise AuthenticationError("Invalid refresh token")

        # Check if expired
        if session.is_expired():
            raise AuthenticationError("Refresh token expired")

        # Get user
        user = await self._users.find_by_id(session.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        # Create new access token
        access_token = self._create_access_token(user)

        # Update session
        session.access_token = access_token
        session.updated_at = datetime.utcnow()
        await self._sessions.save(session)

        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    async def verify_token(self, token: str) -> UserDTO:
        """Verify access token and return user."""
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
            user_id: str = payload.get("sub")
            if not user_id:
                raise AuthenticationError("Invalid token")

            user = await self._users.find_by_id(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")

            return UserDTO(
                id=user.id,
                username=user.username,
                email=str(user.email),
                full_name=user.full_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                roles=user.roles,
                permissions=user.permissions,
                tenant_id=user.tenant_id,
                avatar_url=user.avatar_url,
                last_login=user.last_login,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        except JWTError:
            raise AuthenticationError("Invalid token")

    def _create_access_token(self, user: User) -> str:
        """Create JWT access token."""
        expires = datetime.utcnow() + timedelta(
            minutes=self._settings.access_token_expire_minutes
        )
        payload = {
            "sub": user.id,
            "username": user.username,
            "email": str(user.email),
            "exp": expires,
            "type": "access",
        }
        return jwt.encode(
            payload,
            self._settings.jwt_secret_key,
            algorithm=self._settings.jwt_algorithm,
        )

    def _create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token."""
        expires = datetime.utcnow() + timedelta(
            days=self._settings.refresh_token_expire_days
        )
        payload = {
            "sub": user.id,
            "exp": expires,
            "type": "refresh",
        }
        return jwt.encode(
            payload,
            self._settings.jwt_secret_key,
            algorithm=self._settings.jwt_algorithm,
        )

    def _generate_id(self) -> str:
        """Generate unique ID."""
        from uuid import uuid4

        return str(uuid4())
