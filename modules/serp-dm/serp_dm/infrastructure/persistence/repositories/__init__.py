"""
Repository implementations for Document Management module.
"""

from .postgres import (
    PostgresApprovalRequestRepository,
    PostgresAuditLogRepository,
    PostgresDocumentRepository,
    PostgresDocumentTypeRepository,
    PostgresDocumentVersionRepository,
    PostgresFolderRepository,
    PostgresStageRepository,
    PostgresStorageTemplateRepository,
    PostgresTemplateFolderRepository,
)

__all__ = [
    "PostgresDocumentRepository",
    "PostgresDocumentVersionRepository",
    "PostgresStageRepository",
    "PostgresFolderRepository",
    "PostgresStorageTemplateRepository",
    "PostgresTemplateFolderRepository",
    "PostgresDocumentTypeRepository",
    "PostgresApprovalRequestRepository",
    "PostgresAuditLogRepository",
]
