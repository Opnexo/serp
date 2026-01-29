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
    PostgresStageTemplateRepository,
    PostgresStorageTemplateRepository,
    PostgresTemplateFolderRepository,
)

__all__ = [
    "PostgresDocumentRepository",
    "PostgresDocumentVersionRepository",
    "PostgresStageRepository",
    "PostgresFolderRepository",
    "PostgresStorageTemplateRepository",
    "PostgresStageTemplateRepository",
    "PostgresTemplateFolderRepository",
    "PostgresDocumentTypeRepository",
    "PostgresApprovalRequestRepository",
    "PostgresAuditLogRepository",
]
