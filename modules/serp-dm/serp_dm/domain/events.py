"""
Domain events for Document Management module.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from serp_core.events.domain.base_event import DomainEvent


@dataclass(kw_only=True)
class DocumentRegisteredEvent(DomainEvent):
    """
    Published when a new document is registered in the system.

    Subscribers:
    - Audit logging
    - Search indexing
    - Notifications
    """

    document_id: UUID
    project_id: UUID
    title: str
    document_type_code: str
    created_by: UUID

    @classmethod
    def event_type(cls) -> str:
        return "dm.document.registered"


@dataclass(kw_only=True)
class DocumentVersionUploadedEvent(DomainEvent):
    """
    Published when a new version is uploaded for a document.

    Subscribers:
    - Audit logging
    - Version history indexing
    - Notifications to stakeholders
    """

    document_id: UUID
    version_id: UUID
    version_string: str
    uploaded_by: UUID
    file_size: int

    @classmethod
    def event_type(cls) -> str:
        return "dm.document.version_uploaded"


@dataclass(kw_only=True)
class DocumentStageChangedEvent(DomainEvent):
    """
    Published when a document moves to a different stage (Kanban).

    Subscribers:
    - Audit logging
    - Kanban board updates
    - Workflow notifications
    """

    document_id: UUID
    previous_stage_id: Optional[UUID]
    new_stage_id: UUID
    changed_by: UUID

    @classmethod
    def event_type(cls) -> str:
        return "dm.document.stage_changed"


@dataclass(kw_only=True)
class DocumentApprovedEvent(DomainEvent):
    """
    Published when a document is approved.

    Subscribers:
    - Audit logging
    - Stakeholder notifications
    - Status updates
    """

    document_id: UUID
    approved_by: UUID
    approval_request_id: UUID

    @classmethod
    def event_type(cls) -> str:
        return "dm.document.approved"


@dataclass(kw_only=True)
class DocumentRejectedEvent(DomainEvent):
    """
    Published when a document is rejected.

    Subscribers:
    - Audit logging
    - Author notification
    - Status updates
    """

    document_id: UUID
    rejected_by: UUID
    approval_request_id: UUID
    reason: str = ""

    @classmethod
    def event_type(cls) -> str:
        return "dm.document.rejected"


@dataclass(kw_only=True)
class DocumentArchivedEvent(DomainEvent):
    """
    Published when a document is archived.

    Subscribers:
    - Audit logging
    - Search index removal
    """

    document_id: UUID
    archived_by: UUID

    @classmethod
    def event_type(cls) -> str:
        return "dm.document.archived"


@dataclass(kw_only=True)
class StageCreatedEvent(DomainEvent):
    """Published when a new stage is created for a project."""

    stage_id: UUID
    project_id: UUID
    name: str
    created_by: UUID

    @classmethod
    def event_type(cls) -> str:
        return "dm.stage.created"


@dataclass(kw_only=True)
class FolderCreatedEvent(DomainEvent):
    """Published when a folder is created."""

    folder_id: UUID
    project_id: UUID
    path: str
    created_by: UUID

    @classmethod
    def event_type(cls) -> str:
        return "dm.folder.created"


@dataclass(kw_only=True)
class StorageTemplateAppliedEvent(DomainEvent):
    """Published when a storage template is applied to a project."""

    project_id: UUID
    template_id: UUID
    folders_created: int
    applied_by: UUID

    @classmethod
    def event_type(cls) -> str:
        return "dm.template.applied"
