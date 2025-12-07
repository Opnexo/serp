# SERP Users Module

User management, authentication, and authorization module for the SERP platform.

## Features

- **User Management**: Create, update, delete users
- **Authentication**: JWT-based authentication with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Roles & Permissions**: Fine-grained permission system
- **Password Management**: Secure password hashing with bcrypt
- **Profile Management**: User profiles with customizable fields
- **Tenant Support**: Multi-tenancy support

## Installation

```bash
uv add serp-users
```

## Quick Start

### 1. Register the module

The module auto-registers via entry points. Just install and it's available.

### 2. Configure

```python
# config.py
from serp_users.config import UsersSettings

settings = UsersSettings(
    jwt_secret_key="your-secret-key",
    jwt_algorithm="HS256",
    access_token_expire_minutes=30,
    refresh_token_expire_days=7,
)
```

### 3. Use in your app

```python
from serp_users.application.services import UserService, AuthService
from serp_users.infrastructure.repositories import SQLUserRepository

# Create services
user_repo = SQLUserRepository(db_session)
user_service = UserService(user_repo)
auth_service = AuthService(user_repo)

# Register a user
user = await user_service.create_user(
    username="john",
    email="john@example.com",
    password="secure-password",
    full_name="John Doe"
)

# Authenticate
tokens = await auth_service.login(
    username="john",
    password="secure-password"
)
```

## API Endpoints

All endpoints are registered at `/api/users/*`:

- `POST /api/users/auth/login` - Login user
- `POST /api/users/auth/logout` - Logout user
- `POST /api/users/auth/refresh` - Refresh access token
- `GET /api/users/auth/me` - Get current user
- `GET /api/users` - List users (paginated)
- `GET /api/users/{id}` - Get user by ID
- `POST /api/users` - Create user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `GET /api/users/{id}/permissions` - Get user permissions
- `PUT /api/users/{id}/password` - Change password

## Permissions

Module permissions follow the pattern `users:<action>`:

- `users:list` - List users
- `users:read` - Read user details
- `users:create` - Create users
- `users:update` - Update users
- `users:delete` - Delete users
- `users:manage_roles` - Assign/remove roles
- `users:manage_permissions` - Grant/revoke permissions

## Domain Model

### User (Aggregate Root)

```python
@dataclass
class User(AggregateRoot):
    username: str
    email: str
    password_hash: str
    full_name: str
    is_active: bool
    is_superuser: bool
    roles: List[str]
    permissions: List[str]
    tenant_id: Optional[str]
```

### Role

```python
@dataclass
class Role(Entity):
    name: str
    description: str
    permissions: List[str]
    is_system: bool
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy serp_users

# Linting
uv run ruff check serp_users
```

## License

MIT License - See LICENSE file for details
