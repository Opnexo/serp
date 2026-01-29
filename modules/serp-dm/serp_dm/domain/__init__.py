"""
Domain layer for Document Management module.

Exports all domain entities, value objects, events, and repository interfaces.
"""

# Value Objects
from .value_objects import (
    ApprovalStatus,
    DocumentNumber,
    DocumentStatus,
    DocumentTag,
    FileMetadata,
    FileNamingPattern,
    FilePath,
    Phase,
    StorageKey,
    Version,
    VersionScheme,
)

# Entities
from .entities import (
    ApprovalRequest,
    AuditLogEntry,
    Document,
    DocumentType,
    DocumentVersion,
    Folder,
    Project,
    Stage,
    StageTemplate,
    StageTemplateItem,
    StorageTemplate,
    TemplateFolder,
)

# Repository Interfaces
from .repositories import (
    IApprovalRequestRepository,
    IAuditLogRepository,
    IDocumentRepository,
    IDocumentTypeRepository,
    IDocumentVersionRepository,
    IFolderRepository,
    IProjectRepository,
    IStageRepository,
    IStageTemplateRepository,
    IStorageTemplateRepository,
    ITemplateFolderRepository,
)

# Events
from .events import (
    DocumentApprovedEvent,
    DocumentArchivedEvent,
    DocumentRegisteredEvent,
    DocumentRejectedEvent,
    DocumentStageChangedEvent,
    DocumentVersionUploadedEvent,
    FolderCreatedEvent,
    StageCreatedEvent,
    StorageTemplateAppliedEvent,
)

# Ports
from .ports import IDocumentStorage

__all__ = [
    # Value Objects
    "Version",
    "VersionScheme",
    "DocumentStatus",
    "ApprovalStatus",
    "Phase",
    "DocumentNumber",
    "FileNamingPattern",
    "FileMetadata",
    "FilePath",
    "DocumentTag",
    "StorageKey",
    # Entities
    "Document",
    "DocumentVersion",
    "DocumentType",
    "Stage",
    "Folder",
    "Project",
    "StageTemplate",
    "StageTemplateItem",
    "StorageTemplate",
    "TemplateFolder",
    "ApprovalRequest",
    "AuditLogEntry",
    # Repositories
    "IDocumentRepository",
    "IDocumentVersionRepository",
    "IDocumentTypeRepository",
    "IStageRepository",
    "IFolderRepository",
    "IProjectRepository",
    "IStageTemplateRepository",
    "IStorageTemplateRepository",
    "ITemplateFolderRepository",
    "IApprovalRequestRepository",
    "IAuditLogRepository",
    # Events
    "DocumentRegisteredEvent",
    "DocumentVersionUploadedEvent",
    "DocumentStageChangedEvent",
    "DocumentApprovedEvent",
    "DocumentRejectedEvent",
    "DocumentArchivedEvent",
    "StageCreatedEvent",
    "FolderCreatedEvent",
    "StorageTemplateAppliedEvent",
    # Ports
    "IDocumentStorage",
]
