"""
Domain entities for Document Management module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from serp_core.domain.entity import Entity
from serp_core.domain.aggregate import AggregateRoot


@dataclass
class Document(AggregateRoot):
    """
    Document aggregate root.

    Represents a file/document in the system with metadata and versioning.
    """

    name: str
    folder_id: Optional[UUID]
    file_path: str
    mime_type: str
    size_bytes: int
    checksum: str
    version: int = 1
    description: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_archived: bool = False

    def archive(self) -> None:
        """Mark document as archived."""
        self.is_archived = True

    def restore(self) -> None:
        """Restore document from archive."""
        self.is_archived = False

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """Update document metadata."""
        self.metadata.update(metadata)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the document."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document."""
        if tag in self.tags:
            self.tags.remove(tag)

    def increment_version(self) -> None:
        """Increment document version."""
        self.version += 1


@dataclass
class Folder(Entity):
    """
    Folder entity for organizing documents.

    Supports hierarchical structure with parent-child relationships.
    """

    name: str
    parent_id: Optional[UUID] = None
    description: str = ""
    path: str = "/"
    created_by: Optional[UUID] = None
    is_archived: bool = False

    def archive(self) -> None:
        """Mark folder as archived."""
        self.is_archived = True

    def restore(self) -> None:
        """Restore folder from archive."""
        self.is_archived = False

    def update_path(self, parent_path: str) -> None:
        """Update folder path based on parent."""
        self.path = f"{parent_path}/{self.name}" if parent_path != "/" else f"/{self.name}"


@dataclass
class DocumentVersion(Entity):
    """
    Document version entity.

    Tracks historical versions of a document.
    """

    document_id: UUID
    version_number: int
    file_path: str
    size_bytes: int
    checksum: str
    created_by: UUID
    change_note: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
