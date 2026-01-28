"""
Domain entities for Document Management module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from serp_core.domain.aggregate import AggregateRoot
from serp_core.domain.entity import Entity

from .value_objects import (
    ApprovalStatus,
    DocumentStatus,
    FileNamingPattern,
    Phase,
    StorageKey,
    Version,
    VersionScheme,
)


@dataclass(kw_only=True)
class DocumentType(Entity):
    """
    Configurable document type classification.

    Examples: DRAW (Drawings), CALC (Calculations), TP (Technical Proposal)
    Stored in database for runtime configuration.
    """

    code: str  # Short code like "DRAW", "CALC", "TP"
    name: str  # Display name like "Drawings", "Calculations"
    description: str = ""
    category: str = "general"  # engineering, logistics, finance, contract
    is_active: bool = True


@dataclass(kw_only=True)
class Stage(Entity):
    """
    Document workflow stage (Kanban column) per project.

    Examples: "Opportunity", "Project Won", "Sprint 1", "Deployment"
    """

    project_id: UUID
    name: str
    description: str = ""
    order: int = 0  # Position in Kanban board
    color: str = "#6B7280"  # Hex color for UI
    is_default: bool = False  # New documents start here
    is_active: bool = True


@dataclass(kw_only=True)
class TemplateFolder(Entity):
    """
    Folder definition within a storage template.

    Defines the folder structure that will be created when a project uses the template.
    """

    template_id: UUID
    name: str  # Folder name like "drafts", "engineering"
    path: str  # Full path like "/drafts" or "/engineering/drawings"
    parent_id: Optional[UUID] = None  # For nested folders
    description: str = ""
    order: int = 0  # Display order


@dataclass(kw_only=True)
class StorageTemplate(Entity):
    """
    Storage template defining folder structure for projects.

    Examples: "General", "Scrum", "Infrastructure Architecture"
    """

    name: str
    description: str = ""
    is_default: bool = False  # Used when no template is selected
    is_active: bool = True
    created_by: Optional[UUID] = None
    # Folders are loaded via relationship/repository


@dataclass(kw_only=True)
class Folder(Entity):
    """
    Folder for organizing documents within a project.

    Created from template or manually.
    """

    project_id: UUID
    name: str
    path: str  # Full path from root, e.g., "/engineering/drawings"
    parent_id: Optional[UUID] = None
    description: str = ""
    is_archived: bool = False
    created_by: Optional[UUID] = None


@dataclass(kw_only=True)
class DocumentVersion(Entity):
    """
    Immutable version record for a document.

    Each version has its own physical file stored in MinIO.
    Versions are never modified or deleted (audit trail).
    """

    document_id: UUID
    version: Version  # Version value object (scheme-aware)
    storage_key: StorageKey  # MinIO storage key
    original_filename: str  # Original uploaded filename
    generated_filename: str  # Filename generated from pattern
    mime_type: str
    size_bytes: int
    checksum: str  # SHA-256 hash of file content
    change_note: str = ""  # Description of changes in this version
    uploaded_by: UUID = field(default_factory=lambda: UUID(int=0))  # Placeholder, required
    uploaded_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return f"v{self.version}"


@dataclass(kw_only=True)
class Document(AggregateRoot):
    """
    Document aggregate root - represents a registered document in the DRMS.

    A Document is the logical entity with a title/name that users see.
    It contains multiple versions (physical files) and belongs to a stage.
    """

    # Required fields
    project_id: UUID  # FK to pm.projects
    title: str  # User-facing document name (e.g., "General Architecture")
    document_type_id: UUID  # FK to document_types

    # Auto-generated document number
    document_number: Optional[str] = None  # Generated on first version upload

    # Organization
    folder_id: Optional[UUID] = None  # FK to folders (storage location)
    stage_id: Optional[UUID] = None  # FK to stages (Kanban column)

    # Versioning
    version_scheme: VersionScheme = VersionScheme.SEMANTIC
    current_version: Optional[str] = None  # String representation of latest version

    # Status and metadata
    status: DocumentStatus = DocumentStatus.DRAFT
    description: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    external_references: list[str] = field(default_factory=list)  # Contract/PO numbers

    # Audit fields
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_archived: bool = False

    def move_to_stage(self, stage_id: UUID) -> None:
        """Move document to a different stage."""
        self.stage_id = stage_id

    def move_to_folder(self, folder_id: UUID) -> None:
        """Move document to a different folder."""
        self.folder_id = folder_id

    def archive(self) -> None:
        """Archive the document."""
        self.is_archived = True
        self.status = DocumentStatus.ARCHIVED

    def restore(self) -> None:
        """Restore document from archive."""
        self.is_archived = False
        self.status = DocumentStatus.DRAFT

    def add_tag(self, tag: str) -> None:
        """Add a tag to the document."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document."""
        if tag in self.tags:
            self.tags.remove(tag)

    def add_external_reference(self, reference: str) -> None:
        """Add an external reference (contract/PO number)."""
        if reference not in self.external_references:
            self.external_references.append(reference)

    def update_metadata(self, key: str, value: Any) -> None:
        """Update a metadata field."""
        self.metadata[key] = value

    def submit_for_approval(self) -> None:
        """Submit document for approval workflow."""
        if self.status != DocumentStatus.DRAFT:
            raise ValueError("Only draft documents can be submitted for approval")
        self.status = DocumentStatus.PENDING_APPROVAL

    def approve(self) -> None:
        """Approve the document."""
        if self.status != DocumentStatus.PENDING_APPROVAL:
            raise ValueError("Only pending documents can be approved")
        self.status = DocumentStatus.APPROVED

    def reject(self) -> None:
        """Reject the document."""
        if self.status != DocumentStatus.PENDING_APPROVAL:
            raise ValueError("Only pending documents can be rejected")
        self.status = DocumentStatus.REJECTED

    def supersede(self) -> None:
        """Mark this document as superseded by another."""
        self.status = DocumentStatus.SUPERSEDED


@dataclass(kw_only=True)
class ApprovalRequest(Entity):
    """
    Approval workflow request for a document.

    Tracks approval decisions and history.
    """

    document_id: UUID
    version_string: str  # Version when approval was requested
    requested_by: UUID
    assigned_to: UUID  # Approver user ID
    status: ApprovalStatus = ApprovalStatus.PENDING
    request_note: str = ""  # Note from requester
    decision_note: str = ""  # Note from approver
    requested_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None

    def approve(self, note: str = "") -> None:
        """Approve the request."""
        self.status = ApprovalStatus.APPROVED
        self.decision_note = note
        self.decided_at = datetime.utcnow()

    def reject(self, note: str = "") -> None:
        """Reject the request."""
        self.status = ApprovalStatus.REJECTED
        self.decision_note = note
        self.decided_at = datetime.utcnow()

    def return_for_revision(self, note: str = "") -> None:
        """Return for revision without rejecting."""
        self.status = ApprovalStatus.RETURNED
        self.decision_note = note
        self.decided_at = datetime.utcnow()


@dataclass(kw_only=True)
class AuditLogEntry(Entity):
    """
    Immutable audit log entry.

    Records all system actions for compliance.
    Never modified or deleted.
    """

    action: str  # e.g., "document.created", "version.uploaded", "approval.approved"
    entity_type: str  # e.g., "document", "version", "approval"
    entity_id: UUID
    user_id: UUID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: dict[str, Any] = field(default_factory=dict)  # Additional context
    ip_address: Optional[str] = None
