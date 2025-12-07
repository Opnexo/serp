"""
Permission constants for serp-common module.
"""


class CommonPermissions:
    """Permission constants for common module."""

    # Addresses
    ADDRESS_LIST = "common:addresses:list"
    ADDRESS_READ = "common:addresses:read"
    ADDRESS_CREATE = "common:addresses:create"
    ADDRESS_UPDATE = "common:addresses:update"
    ADDRESS_DELETE = "common:addresses:delete"

    @classmethod
    def all(cls) -> list[str]:
        """Get all permissions."""
        return [
            cls.ADDRESS_LIST,
            cls.ADDRESS_READ,
            cls.ADDRESS_CREATE,
            cls.ADDRESS_UPDATE,
            cls.ADDRESS_DELETE,
        ]
