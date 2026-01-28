"""
Value objects for Document Management module.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any, Optional

from serp_core.domain.value_object import ValueObject


class VersionScheme(str, Enum):
    """Versioning scheme options for documents."""

    SEQUENTIAL = "sequential"  # 0001, 0002, 0003
    SEMANTIC = "semantic"  # x.y.z (1.0.0, 1.0.1, 1.1.0, 2.0.0)
    SIMPLE = "simple"  # x.y (1.0, 1.1, 2.0)


class DocumentStatus(str, Enum):
    """Document lifecycle status."""

    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    MIGRATED = "MIGRATED"
    ARCHIVED = "ARCHIVED"
    CANCELLED = "CANCELLED"


class ApprovalStatus(str, Enum):
    """Approval request status."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RETURNED = "RETURNED"


class Phase(str, Enum):
    """Project lifecycle phase for documents."""

    BID = "990"  # Bid / Tender
    EXECUTION = "001"  # Engineering / Execution


@dataclass(frozen=True)
class Version(ValueObject):
    """
    Immutable version number supporting multiple schemes.

    Depending on scheme:
    - SEQUENTIAL: Uses `sequence` (0001, 0002, ...)
    - SEMANTIC: Uses major.minor.patch (1.0.0, 1.0.1, ...)
    - SIMPLE: Uses major.minor (1.0, 1.1, ...)
    """

    scheme: VersionScheme
    major: int = 0
    minor: int = 0
    patch: int = 0
    sequence: int = 1

    def __post_init__(self) -> None:
        """Validate version numbers are non-negative."""
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError("Version numbers cannot be negative")
        if self.sequence < 1:
            raise ValueError("Sequence must be at least 1")

    def increment_patch(self) -> "Version":
        """Increment patch version (z in x.y.z). For SEQUENTIAL, increments sequence."""
        if self.scheme == VersionScheme.SEQUENTIAL:
            return Version(
                scheme=self.scheme,
                sequence=self.sequence + 1,
            )
        return Version(
            scheme=self.scheme,
            major=self.major,
            minor=self.minor,
            patch=self.patch + 1,
            sequence=self.sequence,
        )

    def increment_minor(self) -> "Version":
        """Increment minor version (y in x.y.z), resets patch to 0."""
        if self.scheme == VersionScheme.SEQUENTIAL:
            return self.increment_patch()
        return Version(
            scheme=self.scheme,
            major=self.major,
            minor=self.minor + 1,
            patch=0,
            sequence=self.sequence,
        )

    def increment_major(self) -> "Version":
        """Increment major version (x in x.y.z), resets minor and patch to 0."""
        if self.scheme == VersionScheme.SEQUENTIAL:
            return self.increment_patch()
        return Version(
            scheme=self.scheme,
            major=self.major + 1,
            minor=0,
            patch=0,
            sequence=self.sequence,
        )

    @classmethod
    def initial(cls, scheme: VersionScheme) -> "Version":
        """Create the initial version for a new document."""
        if scheme == VersionScheme.SEQUENTIAL:
            return cls(scheme=scheme, sequence=1)
        return cls(scheme=scheme, major=1, minor=0, patch=0)

    def __str__(self) -> str:
        """String representation based on scheme."""
        match self.scheme:
            case VersionScheme.SEQUENTIAL:
                return f"{self.sequence:04d}"
            case VersionScheme.SEMANTIC:
                return f"{self.major}.{self.minor}.{self.patch}"
            case VersionScheme.SIMPLE:
                return f"{self.major}.{self.minor}"


@dataclass(frozen=True)
class DocumentNumber(ValueObject):
    """
    Immutable document number following DRMS format.

    Format: ProjectNumber-PhaseCode-DocTypeCode-Sequence-Revision
    Example: F1234567-001-DRAW-0003-001
    """

    project_number: str
    phase_code: str
    doc_type_code: str
    sequence: int
    revision: int
    draft_suffix: Optional[str] = None  # "D00", "D01" for drafts

    def __post_init__(self) -> None:
        """Validate document number components."""
        if not self.project_number:
            raise ValueError("Project number is required")
        if not self.phase_code:
            raise ValueError("Phase code is required")
        if not self.doc_type_code:
            raise ValueError("Document type code is required")
        if self.sequence < 1:
            raise ValueError("Sequence must be at least 1")
        if self.revision < 0:
            raise ValueError("Revision cannot be negative")

    def __str__(self) -> str:
        """Format as document number string."""
        base = f"{self.project_number}-{self.phase_code}-{self.doc_type_code}-{self.sequence:04d}-{self.revision:03d}"
        return f"{base}{self.draft_suffix}" if self.draft_suffix else base


@dataclass(frozen=True)
class FileNamingPattern(ValueObject):
    """
    Configurable file naming pattern with placeholders.

    Available placeholders:
    - {project_name}, {project_number}
    - {document_name}, {document_number}
    - {stage}, {version}, {date}
    - {doc_type}, {phase}, {sequence}, {ext}
    """

    pattern: str

    # Default pattern from requirements
    DEFAULT_PATTERN = "{project_number}-{phase}-{doc_type}-{sequence}-{version}.{ext}"

    def __post_init__(self) -> None:
        """Validate pattern contains at least name and extension."""
        if not self.pattern:
            raise ValueError("Pattern cannot be empty")
        if "{ext}" not in self.pattern:
            raise ValueError("Pattern must contain {ext} placeholder")

    def format(self, context: dict[str, Any]) -> str:
        """
        Generate filename from pattern and context.

        Args:
            context: Dict with placeholder values:
                - project_name, project_number
                - document_name, document_number
                - stage, version, date
                - doc_type, phase, sequence, ext
        """
        result = self.pattern
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                # Sanitize value for filename (remove special chars)
                safe_value = str(value).replace(" ", "_").replace("/", "-")
                result = result.replace(placeholder, safe_value)
        return result

    @classmethod
    def default(cls) -> "FileNamingPattern":
        """Get the default naming pattern."""
        return cls(pattern=cls.DEFAULT_PATTERN)


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


@dataclass(frozen=True)
class StorageKey(ValueObject):
    """
    Storage key for file in MinIO/S3.

    Format: projects/{project_id}/docs/{doc_id}/v{version}/{filename}
    """

    key: str

    def __post_init__(self) -> None:
        """Validate storage key."""
        if not self.key:
            raise ValueError("Storage key cannot be empty")

    @classmethod
    def create(
        cls,
        project_id: str,
        document_id: str,
        version: str,
        filename: str,
    ) -> "StorageKey":
        """Create a storage key from components."""
        key = f"projects/{project_id}/docs/{document_id}/v{version}/{filename}"
        return cls(key=key)
