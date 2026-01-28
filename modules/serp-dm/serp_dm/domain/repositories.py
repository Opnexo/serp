"""
Repository interfaces for Document Management module.

These abstract base classes define the contracts that infrastructure
implementations must fulfill. They are part of the domain layer.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .entities import (
    ApprovalRequest,
    AuditLogEntry,
    Document,
    DocumentType,
    DocumentVersion,
    Folder,
    Stage,
    StorageTemplate,
    TemplateFolder,
)
from .value_objects import ApprovalStatus, DocumentStatus, Phase


class IDocumentRepository(ABC):
    """Repository interface for Document aggregate."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Document]:
        """Get document by ID."""
        ...

    @abstractmethod
    async def get_by_document_number(self, number: str) -> Optional[Document]:
        """Get document by its unique document number."""
        ...

    @abstractmethod
    async def list_by_project(
        self,
        project_id: UUID,
        folder_id: Optional[UUID] = None,
        stage_id: Optional[UUID] = None,
        status: Optional[DocumentStatus] = None,
        document_type_id: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Document]:
        """List documents by project with optional filters."""
        ...

    @abstractmethod
    async def count_by_project(
        self,
        project_id: UUID,
        folder_id: Optional[UUID] = None,
        stage_id: Optional[UUID] = None,
        status: Optional[DocumentStatus] = None,
        document_type_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count documents matching filters."""
        ...

    @abstractmethod
    async def get_next_sequence(
        self,
        project_id: UUID,
        phase: Phase,
        doc_type_code: str,
    ) -> int:
        """Get the next sequence number for document numbering."""
        ...

    @abstractmethod
    async def save(self, document: Document) -> Document:
        """Save (insert or update) a document."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a document (soft delete via archive)."""
        ...


class IDocumentVersionRepository(ABC):
    """Repository interface for DocumentVersion entity."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[DocumentVersion]:
        """Get version by ID."""
        ...

    @abstractmethod
    async def get_latest(self, document_id: UUID) -> Optional[DocumentVersion]:
        """Get the latest version of a document."""
        ...

    @abstractmethod
    async def list_by_document(
        self,
        document_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[DocumentVersion]:
        """List all versions of a document, newest first."""
        ...

    @abstractmethod
    async def count_by_document(self, document_id: UUID) -> int:
        """Count versions for a document."""
        ...

    @abstractmethod
    async def save(self, version: DocumentVersion) -> DocumentVersion:
        """Save a new version (versions are immutable, no updates)."""
        ...


class IStageRepository(ABC):
    """Repository interface for Stage entity (Kanban columns)."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Stage]:
        """Get stage by ID."""
        ...

    @abstractmethod
    async def get_default(self, project_id: UUID) -> Optional[Stage]:
        """Get the default stage for new documents in a project."""
        ...

    @abstractmethod
    async def list_by_project(self, project_id: UUID) -> list[Stage]:
        """List all stages for a project, ordered by position."""
        ...

    @abstractmethod
    async def save(self, stage: Stage) -> Stage:
        """Save (insert or update) a stage."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a stage (only if no documents are in it)."""
        ...

    @abstractmethod
    async def reorder(self, project_id: UUID, stage_ids: list[UUID]) -> None:
        """Reorder stages based on new order of IDs."""
        ...


class IFolderRepository(ABC):
    """Repository interface for Folder entity."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Folder]:
        """Get folder by ID."""
        ...

    @abstractmethod
    async def get_by_path(self, project_id: UUID, path: str) -> Optional[Folder]:
        """Get folder by its path within a project."""
        ...

    @abstractmethod
    async def list_by_project(
        self,
        project_id: UUID,
        parent_id: Optional[UUID] = None,
    ) -> list[Folder]:
        """List folders, optionally under a parent."""
        ...

    @abstractmethod
    async def save(self, folder: Folder) -> Folder:
        """Save (insert or update) a folder."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a folder (only if empty)."""
        ...


class IStorageTemplateRepository(ABC):
    """Repository interface for StorageTemplate entity."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[StorageTemplate]:
        """Get template by ID."""
        ...

    @abstractmethod
    async def get_default(self) -> Optional[StorageTemplate]:
        """Get the default template."""
        ...

    @abstractmethod
    async def list_all(self, include_inactive: bool = False) -> list[StorageTemplate]:
        """List all templates."""
        ...

    @abstractmethod
    async def save(self, template: StorageTemplate) -> StorageTemplate:
        """Save (insert or update) a template."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a template (only if not in use)."""
        ...


class ITemplateFolderRepository(ABC):
    """Repository interface for TemplateFolder entity."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[TemplateFolder]:
        """Get template folder by ID."""
        ...

    @abstractmethod
    async def list_by_template(self, template_id: UUID) -> list[TemplateFolder]:
        """List all folders in a template."""
        ...

    @abstractmethod
    async def save(self, folder: TemplateFolder) -> TemplateFolder:
        """Save a template folder."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a template folder."""
        ...


class IDocumentTypeRepository(ABC):
    """Repository interface for DocumentType entity."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[DocumentType]:
        """Get document type by ID."""
        ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[DocumentType]:
        """Get document type by code."""
        ...

    @abstractmethod
    async def list_all(
        self,
        category: Optional[str] = None,
        include_inactive: bool = False,
    ) -> list[DocumentType]:
        """List all document types."""
        ...

    @abstractmethod
    async def save(self, doc_type: DocumentType) -> DocumentType:
        """Save (insert or update) a document type."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a document type (only if not in use)."""
        ...


class IApprovalRequestRepository(ABC):
    """Repository interface for ApprovalRequest entity."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[ApprovalRequest]:
        """Get approval request by ID."""
        ...

    @abstractmethod
    async def list_by_document(self, document_id: UUID) -> list[ApprovalRequest]:
        """List all approval requests for a document."""
        ...

    @abstractmethod
    async def list_pending_for_user(self, user_id: UUID) -> list[ApprovalRequest]:
        """List pending approvals assigned to a user."""
        ...

    @abstractmethod
    async def list_by_status(
        self,
        status: ApprovalStatus,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ApprovalRequest]:
        """List approvals by status."""
        ...

    @abstractmethod
    async def save(self, request: ApprovalRequest) -> ApprovalRequest:
        """Save an approval request."""
        ...


class IAuditLogRepository(ABC):
    """Repository interface for AuditLogEntry (append-only)."""

    @abstractmethod
    async def log(self, entry: AuditLogEntry) -> AuditLogEntry:
        """Append an audit log entry (immutable, no updates/deletes)."""
        ...

    @abstractmethod
    async def list_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        """List audit entries for an entity."""
        ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        """List audit entries by user."""
        ...

    @abstractmethod
    async def search(
        self,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        user_id: Optional[UUID] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        """Search audit logs with filters."""
        ...
