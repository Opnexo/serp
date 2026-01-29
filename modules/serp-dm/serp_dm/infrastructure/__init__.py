"""Infrastructure layer __init__.py"""

from serp_dm.infrastructure.persistence.repositories.memory import (
    InMemoryApprovalRequestRepository,
    InMemoryAuditLogRepository,
    InMemoryDocumentRepository,
    InMemoryDocumentTypeRepository,
    InMemoryDocumentVersionRepository,
    InMemoryFolderRepository,
    InMemoryProjectRepository,
    InMemoryStageRepository,
    InMemoryStageTemplateRepository,
    InMemoryStorageTemplateRepository,
    InMemoryTemplateFolderRepository,
)
from serp_dm.infrastructure.persistence.repositories.postgres import (
    PostgresApprovalRequestRepository,
    PostgresAuditLogRepository,
    PostgresDocumentRepository,
    PostgresDocumentTypeRepository,
    PostgresDocumentVersionRepository,
    PostgresFolderRepository,
    PostgresProjectRepository,
    PostgresStageRepository,
    PostgresStageTemplateRepository,
    PostgresStorageTemplateRepository,
    PostgresTemplateFolderRepository,
)
from serp_dm.infrastructure.storage.minio_adapter import MinioStorageAdapter

__all__ = [
    # Postgres Repositories
    "PostgresDocumentRepository",
    "PostgresDocumentVersionRepository",
    "PostgresStageRepository",
    "PostgresFolderRepository",
    "PostgresProjectRepository",
    "PostgresStageTemplateRepository",
    "PostgresStorageTemplateRepository",
    "PostgresTemplateFolderRepository",
    "PostgresDocumentTypeRepository",
    "PostgresApprovalRequestRepository",
    "PostgresAuditLogRepository",
    # In-Memory Repositories (for testing)
    "InMemoryDocumentRepository",
    "InMemoryDocumentVersionRepository",
    "InMemoryStageRepository",
    "InMemoryFolderRepository",
    "InMemoryProjectRepository",
    "InMemoryStageTemplateRepository",
    "InMemoryStorageTemplateRepository",
    "InMemoryTemplateFolderRepository",
    "InMemoryDocumentTypeRepository",
    "InMemoryApprovalRequestRepository",
    "InMemoryAuditLogRepository",
    # Storage
    "MinioStorageAdapter",
]
