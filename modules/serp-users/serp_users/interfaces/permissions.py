"""Permission definitions for users module."""

# User permissions
USERS_LIST = "users:list"
USERS_READ = "users:read"
USERS_CREATE = "users:create"
USERS_UPDATE = "users:update"
USERS_DELETE = "users:delete"
USERS_MANAGE_ROLES = "users:manage_roles"
USERS_MANAGE_PERMISSIONS = "users:manage_permissions"

# All permissions
ALL_PERMISSIONS = [
    USERS_LIST,
    USERS_READ,
    USERS_CREATE,
    USERS_UPDATE,
    USERS_DELETE,
    USERS_MANAGE_ROLES,
    USERS_MANAGE_PERMISSIONS,
]
