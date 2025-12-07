"""
Application layer exceptions
"""


class ApplicationError(Exception):
    """Base exception for application errors"""

    pass


class ValidationError(ApplicationError):
    """Raised when validation fails"""

    def __init__(self, message: str, errors: dict = None):
        self.errors = errors or {}
        super().__init__(message)


class ConfigurationError(ApplicationError):
    """Raised when configuration is invalid"""

    pass
