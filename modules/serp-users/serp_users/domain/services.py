"""Domain services for users module."""

from passlib.context import CryptContext


class PasswordHasher:
    """Service for password hashing and verification."""

    def __init__(self) -> None:
        self._context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        """Hash a password."""
        return self._context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return self._context.verify(plain_password, hashed_password)

    def needs_rehash(self, hashed_password: str) -> bool:
        """Check if password hash needs to be updated."""
        return self._context.needs_update(hashed_password)
