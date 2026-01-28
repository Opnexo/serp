"""
Data Transfer Objects for Document Management module.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# =============================================================================
# Request DTOs
# =============================================================================


class RegisterDocumentRequest(BaseModel):
    """Request to register a new document."""

    project_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    document_type_id: UUID
    folder_id: Optional[UUID] = None
    stage_id: Optional[UUID] = None
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_references: list[str] = Field(default_factory=list)


class UpdateDocumentRequest(BaseModel):
    """Request to update a document."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    folder_id: Optional[UUID] = None
    stage_id: Optional[UUID] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None
    external_references: Optional[list[str]] = None


class UploadVersionRequest(BaseModel):
    """Request to upload a new version (metadata only, file is separate)."""

    change_note: str = ""
    bump_type: str = "patch"  # "patch", "minor", "major"


class CreateStageRequest(BaseModel):
    """Request to create a new stage."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    color: str = "#6B7280"
    is_default: bool = False


class UpdateStageRequest(BaseModel):
    """Request to update a stage."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = None


class ReorderStagesRequest(BaseModel):
    """Request to reorder stages."""

    stage_ids: list[UUID]


class CreateFolderRequest(BaseModel):
    """Request to create a new folder."""

    project_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: Optional[UUID] = None
    description: str = ""


class CreateStorageTemplateRequest(BaseModel):
    """Request to create a storage template."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    is_default: bool = False
    folders: list[dict[str, Any]] = Field(default_factory=list)  # [{name, path, description}]


class CreateDocumentTypeRequest(BaseModel):
    """Request to create a document type."""

    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    category: str = "general"


class UpdateDocumentTypeRequest(BaseModel):
    """Request to update a document type."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class MoveDocumentRequest(BaseModel):
    """Request to move document to a different stage or folder."""

    stage_id: Optional[UUID] = None
    folder_id: Optional[UUID] = None


class SubmitForApprovalRequest(BaseModel):
    """Request to submit document for approval."""

    assigned_to: UUID
    request_note: str = ""


class ApprovalDecisionRequest(BaseModel):
    """Request to make an approval decision."""

    decision: str  # "approve", "reject", "return"
    decision_note: str = ""


# =============================================================================
# Response DTOs
# =============================================================================


class DocumentDTO(BaseModel):
    """Document data transfer object."""

    id: UUID
    project_id: UUID
    title: str
    document_number: Optional[str]
    document_type_id: UUID
    document_type_code: Optional[str] = None
    document_type_name: Optional[str] = None
    folder_id: Optional[UUID]
    folder_path: Optional[str] = None
    stage_id: Optional[UUID]
    stage_name: Optional[str] = None
    stage_color: Optional[str] = None
    version_scheme: str
    current_version: Optional[str]
    status: str
    description: str
    tags: list[str]
    metadata: dict[str, Any]
    external_references: list[str]
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentVersionDTO(BaseModel):
    """Document version data transfer object."""

    id: UUID
    document_id: UUID
    version_string: str
    original_filename: str
    generated_filename: str
    mime_type: str
    size_bytes: int
    checksum: str
    change_note: str
    uploaded_by: UUID
    uploaded_at: datetime
    download_url: Optional[str] = None  # Presigned URL for download

    model_config = {"from_attributes": True}


class StageDTO(BaseModel):
    """Stage data transfer object."""

    id: UUID
    project_id: UUID
    name: str
    description: str
    order: int
    color: str
    is_default: bool
    document_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FolderDTO(BaseModel):
    """Folder data transfer object."""

    id: UUID
    project_id: UUID
    name: str
    path: str
    parent_id: Optional[UUID]
    description: str
    document_count: int = 0
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StorageTemplateDTO(BaseModel):
    """Storage template data transfer object."""

    id: UUID
    name: str
    description: str
    is_default: bool
    is_active: bool
    folder_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TemplateFolderDTO(BaseModel):
    """Template folder data transfer object."""

    id: UUID
    template_id: UUID
    name: str
    path: str
    parent_id: Optional[UUID]
    description: str
    order: int

    model_config = {"from_attributes": True}


class DocumentTypeDTO(BaseModel):
    """Document type data transfer object."""

    id: UUID
    code: str
    name: str
    description: str
    category: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApprovalRequestDTO(BaseModel):
    """Approval request data transfer object."""

    id: UUID
    document_id: UUID
    document_title: Optional[str] = None
    version_string: str
    requested_by: UUID
    assigned_to: UUID
    status: str
    request_note: str
    decision_note: str
    requested_at: datetime
    decided_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AuditLogDTO(BaseModel):
    """Audit log entry data transfer object."""

    id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    user_id: UUID
    timestamp: datetime
    details: dict[str, Any]
    ip_address: Optional[str]

    model_config = {"from_attributes": True}


# =============================================================================
# List/Pagination Response DTOs
# =============================================================================


class PaginatedResponse(BaseModel):
    """Base paginated response."""

    total: int
    page: int = 1
    page_size: int = 50
    has_more: bool = False


class DocumentListResponse(PaginatedResponse):
    """Paginated list of documents."""

    items: list[DocumentDTO]


class StageListResponse(BaseModel):
    """List of stages."""

    items: list[StageDTO]


class FolderTreeResponse(BaseModel):
    """Folder tree structure."""

    items: list[FolderDTO]


class KanbanBoardResponse(BaseModel):
    """Kanban board data for project."""

    project_id: UUID
    stages: list[StageDTO]
    documents_by_stage: dict[str, list[DocumentDTO]]  # stage_id -> documents


class ExportResponse(BaseModel):
    """Response for export operation."""

    download_url: str
    expires_at: datetime
    filename: str
    size_bytes: int
