"""Infrastructure layer __init__.py"""

from serp_dm.infrastructure.persistence.repositories.postgres import (
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
from serp_dm.infrastructure.storage.minio_adapter import MinioStorageAdapter

__all__ = [
    # Repositories
    "PostgresDocumentRepository",
    "PostgresDocumentVersionRepository",
    "PostgresStageRepository",
    "PostgresFolderRepository",
    "PostgresStorageTemplateRepository",
    "PostgresTemplateFolderRepository",
    "PostgresDocumentTypeRepository",
    "PostgresApprovalRequestRepository",
    "PostgresAuditLogRepository",
    # Storage
    "MinioStorageAdapter",
]
