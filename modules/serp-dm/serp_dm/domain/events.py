"""
Domain events for Document Management module.
"""

from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from serp_core.events.domain.base_event import DomainEvent


@dataclass
class DocumentCreatedEvent(DomainEvent):
    """
    Event raised when a document is created.
    """

    document_id: UUID
    name: str
    folder_id: Optional[UUID]
    mime_type: str
    size_bytes: int
    created_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "dm.document.created"


@dataclass
class DocumentUpdatedEvent(DomainEvent):
    """
    Event raised when a document is updated.
    """

    document_id: UUID
    name: str
    updated_by: Optional[UUID]
    changes: dict[str, Any]

    @property
    def event_type(self) -> str:
        return "dm.document.updated"


@dataclass
class DocumentDeletedEvent(DomainEvent):
    """
    Event raised when a document is deleted.
    """

    document_id: UUID
    name: str
    deleted_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "dm.document.deleted"


@dataclass
class DocumentArchivedEvent(DomainEvent):
    """
    Event raised when a document is archived.
    """

    document_id: UUID
    name: str
    archived_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "dm.document.archived"


@dataclass
class FolderCreatedEvent(DomainEvent):
    """
    Event raised when a folder is created.
    """

    folder_id: UUID
    name: str
    parent_id: Optional[UUID]
    created_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "dm.folder.created"


@dataclass
class FolderDeletedEvent(DomainEvent):
    """
    Event raised when a folder is deleted.
    """

    folder_id: UUID
    name: str
    deleted_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "dm.folder.deleted"
