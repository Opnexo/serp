"""
Value objects for Document Management module.
"""

from dataclasses import dataclass
from typing import Optional

from serp_core.domain.value_object import ValueObject


@dataclass(frozen=True)
class FileMetadata(ValueObject):
    """
    File metadata value object.

    Contains immutable file information.
    """

    file_name: str
    mime_type: str
    size_bytes: int
    checksum: str
    extension: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate file metadata."""
        if self.size_bytes < 0:
            raise ValueError("File size cannot be negative")
        if not self.file_name:
            raise ValueError("File name cannot be empty")
        if not self.checksum:
            raise ValueError("Checksum is required")


@dataclass(frozen=True)
class FilePath(ValueObject):
    """
    File path value object.

    Represents a validated file path.
    """

    path: str

    def __post_init__(self) -> None:
        """Validate file path."""
        if not self.path:
            raise ValueError("Path cannot be empty")
        if ".." in self.path:
            raise ValueError("Path cannot contain '..' for security reasons")

    @property
    def directory(self) -> str:
        """Get directory part of the path."""
        return "/".join(self.path.split("/")[:-1]) or "/"

    @property
    def filename(self) -> str:
        """Get filename part of the path."""
        return self.path.split("/")[-1]


@dataclass(frozen=True)
class DocumentTag(ValueObject):
    """
    Document tag value object.

    Represents a validated tag.
    """

    name: str

    def __post_init__(self) -> None:
        """Validate tag."""
        if not self.name:
            raise ValueError("Tag name cannot be empty")
        if len(self.name) > 50:
            raise ValueError("Tag name cannot exceed 50 characters")
        if not self.name.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Tag can only contain alphanumeric characters, hyphens, and underscores")
