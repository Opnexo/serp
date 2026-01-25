"""
Data Transfer Objects for Document Management module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Request DTOs
class CreateDocumentRequest(BaseModel):
    """Request to create a new document."""

    name: str = Field(..., min_length=1, max_length=255)
    folder_id: Optional[UUID] = None
    file_path: str
    mime_type: str
    size_bytes: int = Field(..., gt=0)
    checksum: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateDocumentRequest(BaseModel):
    """Request to update a document."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    folder_id: Optional[UUID] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class CreateFolderRequest(BaseModel):
    """Request to create a new folder."""

    name: str = Field(..., min_length=1, max_length=255)
    parent_id: Optional[UUID] = None
    description: str = ""


class UpdateFolderRequest(BaseModel):
    """Request to update a folder."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


# Response DTOs
class DocumentDTO(BaseModel):
    """Document data transfer object."""

    id: UUID
    name: str
    folder_id: Optional[UUID]
    file_path: str
    mime_type: str
    size_bytes: int
    checksum: str
    version: int
    description: str
    tags: list[str]
    metadata: dict[str, Any]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FolderDTO(BaseModel):
    """Folder data transfer object."""

    id: UUID
    name: str
    parent_id: Optional[UUID]
    description: str
    path: str
    created_by: Optional[UUID]
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentVersionDTO(BaseModel):
    """Document version data transfer object."""

    id: UUID
    document_id: UUID
    version_number: int
    file_path: str
    size_bytes: int
    checksum: str
    created_by: UUID
    change_note: str
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# List/Pagination Response DTOs
class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    items: list[DocumentDTO]
    total: int
    page: int = 1
    page_size: int = 50
    has_more: bool = False


class FolderListResponse(BaseModel):
    """Paginated list of folders."""

    items: list[FolderDTO]
    total: int
    page: int = 1
    page_size: int = 50
    has_more: bool = False


class DocumentSearchRequest(BaseModel):
    """Request to search documents."""

    query: str
    folder_id: Optional[UUID] = None
    tags: Optional[list[str]] = None
    mime_types: Optional[list[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)
