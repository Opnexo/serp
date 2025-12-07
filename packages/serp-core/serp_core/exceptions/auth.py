"""
Authentication and authorization exceptions
"""


class AuthenticationError(Exception):
    """Base exception for authentication errors"""

    pass


class PermissionDeniedError(AuthenticationError):
    """Raised when user lacks required permissions"""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""

    pass


class TokenExpiredError(AuthenticationError):
    """Raised when authentication token has expired"""

    pass
