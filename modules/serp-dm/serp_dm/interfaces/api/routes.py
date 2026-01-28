"""
FastAPI routes for Document Management module.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from serp_dm.application.dto import (
    CreateDocumentTypeRequest,
    CreateFolderRequest,
    CreateStageRequest,
    CreateStorageTemplateRequest,
    DocumentDTO,
    DocumentListResponse,
    DocumentTypeDTO,
    DocumentVersionDTO,
    FolderDTO,
    FolderTreeResponse,
    KanbanBoardResponse,
    MoveDocumentRequest,
    RegisterDocumentRequest,
    ReorderStagesRequest,
    StageDTO,
    StageListResponse,
    StorageTemplateDTO,
    UpdateDocumentRequest,
    UpdateDocumentTypeRequest,
    UpdateStageRequest,
)
from serp_dm.interfaces.permissions import DMPermissions
from serp_dm.application.services import (
    DocumentService,
    VersioningService,
    StageService,
    FolderService,
    DocumentTypeService,
    StorageTemplateService,
)
from serp_dm.infrastructure.persistence.database import get_db_session
from serp_dm.infrastructure.persistence.repositories.postgres import (
    PostgresDocumentRepository,
    PostgresDocumentVersionRepository,
    PostgresStageRepository,
    PostgresFolderRepository,
    PostgresDocumentTypeRepository,
    PostgresStorageTemplateRepository,
    PostgresTemplateFolderRepository,
    PostgresApprovalRequestRepository,
    PostgresAuditLogRepository,
)
from serp_dm.infrastructure.storage import MinioStorageAdapter
from sqlalchemy.ext.asyncio import AsyncSession

# Main router
router = APIRouter(tags=["Document Management"])


# =============================================================================
# Dependency Injection
# =============================================================================

def get_document_service(session: AsyncSession = Depends(get_db_session)) -> DocumentService:
    """Get document service instance."""
    storage = MinioStorageAdapter()  # Uses default MinIO settings
    return DocumentService(
        document_repo=PostgresDocumentRepository(session),
        version_repo=PostgresDocumentVersionRepository(session),
        stage_repo=PostgresStageRepository(session),
        folder_repo=PostgresFolderRepository(session),
        doc_type_repo=PostgresDocumentTypeRepository(session),
        storage=storage,
        audit_repo=PostgresAuditLogRepository(session),
    )


def get_versioning_service(session: AsyncSession = Depends(get_db_session)) -> VersioningService:
    """Get versioning service instance."""
    storage = MinioStorageAdapter()  # Uses default MinIO settings
    return VersioningService(
        document_repo=PostgresDocumentRepository(session),
        version_repo=PostgresDocumentVersionRepository(session),
        doc_type_repo=PostgresDocumentTypeRepository(session),
        storage=storage,
        audit_repo=PostgresAuditLogRepository(session),
    )


def get_stage_service(session: AsyncSession = Depends(get_db_session)) -> StageService:
    """Get stage service instance."""
    return StageService(
        stage_repo=PostgresStageRepository(session),
        document_repo=PostgresDocumentRepository(session),
    )


def get_folder_service(session: AsyncSession = Depends(get_db_session)) -> FolderService:
    """Get folder service instance."""
    return FolderService(
        folder_repo=PostgresFolderRepository(session),
    )


def get_doc_type_service(session: AsyncSession = Depends(get_db_session)) -> DocumentTypeService:
    """Get document type service instance."""
    return DocumentTypeService(
        doc_type_repo=PostgresDocumentTypeRepository(session),
    )


def get_template_service(session: AsyncSession = Depends(get_db_session)) -> StorageTemplateService:
    """Get storage template service instance."""
    return StorageTemplateService(
        template_repo=PostgresStorageTemplateRepository(session),
        template_folder_repo=PostgresTemplateFolderRepository(session),
        folder_repo=PostgresFolderRepository(session),
    )


async def get_current_user_id() -> UUID:
    """Get current authenticated user ID."""
    # TODO: Extract from auth context
    # For now, return a placeholder UUID
    import uuid
    return uuid.UUID("00000000-0000-0000-0000-000000000000")


# =============================================================================
# Document Routes
# =============================================================================


@router.get(
    "/projects/{project_id}/documents",
    response_model=DocumentListResponse,
    summary="List documents in project",
)
async def list_documents(
    project_id: UUID,
    folder_id: Optional[UUID] = None,
    stage_id: Optional[UUID] = None,
    status: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search in title, number, description"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service=Depends(get_document_service),
):
    """List all documents in a project with optional filters."""
    return await service.list_documents(
        project_id=project_id,
        folder_id=folder_id,
        stage_id=stage_id,
        status=status,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentDTO,
    summary="Get document by ID",
)
async def get_document(
    document_id: UUID,
    service=Depends(get_document_service),
):
    """Get document details by ID."""
    document = await service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post(
    "/projects/{project_id}/documents",
    response_model=DocumentDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new document",
)
async def register_document(
    project_id: UUID,
    request: RegisterDocumentRequest,
    service=Depends(get_document_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Register a new document in the project."""
    request.project_id = project_id
    return await service.register_document(request, user_id)


@router.put(
    "/documents/{document_id}",
    response_model=DocumentDTO,
    summary="Update document metadata",
)
async def update_document(
    document_id: UUID,
    request: UpdateDocumentRequest,
    service=Depends(get_document_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update document metadata."""
    document = await service.update_document(document_id, request, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archive/delete a document",
)
async def delete_document(
    document_id: UUID,
    service=Depends(get_document_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Archive (soft delete) a document."""
    success = await service.delete_document(document_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@router.put(
    "/documents/{document_id}/move",
    response_model=DocumentDTO,
    summary="Move document to different stage/folder",
)
async def move_document(
    document_id: UUID,
    request: MoveDocumentRequest,
    service=Depends(get_document_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Move document to a different stage or folder."""
    document = await service.move_document(document_id, request, user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


# =============================================================================
# Version Routes
# =============================================================================


@router.get(
    "/documents/{document_id}/versions",
    response_model=list[DocumentVersionDTO],
    summary="List document versions",
)
async def list_versions(
    document_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    service=Depends(get_versioning_service),
):
    """List all versions of a document, newest first."""
    return await service.list_versions(document_id, page, page_size)


@router.post(
    "/documents/{document_id}/versions",
    response_model=DocumentVersionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Upload new version",
)
async def upload_version(
    document_id: UUID,
    file: UploadFile = File(...),
    change_note: str = "",
    bump_type: str = Query("patch", enum=["patch", "minor", "major"]),
    service=Depends(get_versioning_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Upload a new version of the document."""
    content = await file.read()
    return await service.upload_version(
        document_id=document_id,
        file_content=content,
        original_filename=file.filename or "unknown",
        mime_type=file.content_type or "application/octet-stream",
        user_id=user_id,
        change_note=change_note,
        bump_type=bump_type,
    )


@router.get(
    "/versions/{version_id}",
    response_model=DocumentVersionDTO,
    summary="Get version details",
)
async def get_version(
    version_id: UUID,
    service=Depends(get_versioning_service),
):
    """Get version details including download URL."""
    version = await service.get_version(version_id)
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return version


@router.get(
    "/versions/{version_id}/download",
    summary="Get presigned download URL",
)
async def get_download_url(
    version_id: UUID,
    service=Depends(get_versioning_service),
):
    """Get a presigned URL to download the version file."""
    url = await service.get_download_url(version_id)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return {"download_url": url}


# =============================================================================
# Stage (Kanban) Routes
# =============================================================================


@router.get(
    "/projects/{project_id}/stages",
    response_model=StageListResponse,
    summary="List project stages",
)
async def list_stages(
    project_id: UUID,
    service=Depends(get_stage_service),
):
    """List all stages (Kanban columns) for a project."""
    stages = await service.list_stages(project_id)
    return StageListResponse(items=stages)


@router.post(
    "/projects/{project_id}/stages",
    response_model=StageDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a stage",
)
async def create_stage(
    project_id: UUID,
    request: CreateStageRequest,
    service=Depends(get_stage_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a new stage for the project."""
    return await service.create_stage(project_id, request, user_id)


@router.put(
    "/stages/{stage_id}",
    response_model=StageDTO,
    summary="Update a stage",
)
async def update_stage(
    stage_id: UUID,
    request: UpdateStageRequest,
    service=Depends(get_stage_service),
):
    """Update stage details."""
    stage = await service.update_stage(stage_id, request)
    if not stage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")
    return stage


@router.put(
    "/projects/{project_id}/stages/reorder",
    response_model=StageListResponse,
    summary="Reorder stages",
)
async def reorder_stages(
    project_id: UUID,
    request: ReorderStagesRequest,
    service=Depends(get_stage_service),
):
    """Reorder stages by providing new order of stage IDs."""
    stages = await service.reorder_stages(project_id, request.stage_ids)
    return StageListResponse(items=stages)


@router.get(
    "/projects/{project_id}/kanban",
    response_model=KanbanBoardResponse,
    summary="Get Kanban board data",
)
async def get_kanban_board(
    project_id: UUID,
    service=Depends(get_stage_service),
):
    """Get full Kanban board with stages and documents."""
    return await service.get_kanban_board(project_id)


# =============================================================================
# Folder Routes
# =============================================================================


@router.get(
    "/projects/{project_id}/folders",
    response_model=FolderTreeResponse,
    summary="List project folders",
)
async def list_folders(
    project_id: UUID,
    parent_id: Optional[UUID] = None,
    service=Depends(get_folder_service),
):
    """List folders in a project, optionally under a parent."""
    folders = await service.list_folders(project_id, parent_id)
    return FolderTreeResponse(items=folders)


@router.post(
    "/projects/{project_id}/folders",
    response_model=FolderDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a folder",
)
async def create_folder(
    project_id: UUID,
    request: CreateFolderRequest,
    service=Depends(get_folder_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a new folder in the project."""
    request.project_id = project_id
    return await service.create_folder(request, user_id)


# =============================================================================
# Document Type Routes (Admin)
# =============================================================================


@router.get(
    "/admin/document-types",
    response_model=list[DocumentTypeDTO],
    summary="List document types",
)
async def list_document_types(
    category: Optional[str] = None,
    include_inactive: bool = False,
    service=Depends(get_doc_type_service),
):
    """List all document types."""
    return await service.list_types(category, include_inactive)


@router.post(
    "/admin/document-types",
    response_model=DocumentTypeDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a document type",
)
async def create_document_type(
    request: CreateDocumentTypeRequest,
    service=Depends(get_doc_type_service),
):
    """Create a new document type (admin only)."""
    return await service.create_type(request)


@router.put(
    "/admin/document-types/{type_id}",
    response_model=DocumentTypeDTO,
    summary="Update a document type",
)
async def update_document_type(
    type_id: UUID,
    request: UpdateDocumentTypeRequest,
    service=Depends(get_doc_type_service),
):
    """Update a document type (admin only)."""
    doc_type = await service.update_type(type_id, request)
    if not doc_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document type not found")
    return doc_type


# =============================================================================
# Storage Template Routes (Admin)
# =============================================================================


@router.get(
    "/admin/templates",
    response_model=list[StorageTemplateDTO],
    summary="List storage templates",
)
async def list_templates(
    include_inactive: bool = False,
    service=Depends(get_template_service),
):
    """List all storage templates."""
    return await service.list_templates(include_inactive)


@router.post(
    "/admin/templates",
    response_model=StorageTemplateDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a storage template",
)
async def create_template(
    request: CreateStorageTemplateRequest,
    service=Depends(get_template_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a new storage template (admin only)."""
    return await service.create_template(request, user_id)


@router.post(
    "/projects/{project_id}/apply-template/{template_id}",
    response_model=list[FolderDTO],
    summary="Apply template to project",
)
async def apply_template(
    project_id: UUID,
    template_id: UUID,
    service=Depends(get_template_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """Apply a storage template to create folders in a project."""
    return await service.apply_template(project_id, template_id, user_id)


# =============================================================================
# Export Routes
# =============================================================================


@router.get(
    "/projects/{project_id}/export",
    summary="Export project documents as ZIP",
)
async def export_project_documents(
    project_id: UUID,
    include_all_versions: bool = Query(False, description="Include all versions or just latest"),
    folder_id: Optional[UUID] = Query(None, description="Export only from specific folder"),
    service=Depends(get_document_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Export all project documents as a ZIP file.
    
    Returns a presigned URL to download the ZIP file.
    """
    from fastapi.responses import StreamingResponse
    import io
    import zipfile
    
    # Get all documents for project
    documents = await service.list_documents(
        project_id=project_id,
        folder_id=folder_id,
    )
    
    if not documents.items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found in project"
        )
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for doc in documents.items:
            if not doc.current_version:
                continue
            
            # Get file content from storage
            # In production, would stream from MinIO
            filename = f"{doc.document_number or doc.title}_{doc.current_version.version_string}"
            filename = filename.replace(" ", "_").replace("/", "_")
            
            # Add metadata file for each document
            metadata = f"""Document: {doc.title}
Number: {doc.document_number or 'N/A'}
Type: {doc.document_type.name if doc.document_type else 'Unknown'}
Status: {doc.status}
Version: {doc.current_version.version_string}
Created: {doc.created_at}
"""
            zip_file.writestr(f"{filename}_metadata.txt", metadata)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=project_{project_id}_documents.zip"
        }
    )


# =============================================================================
# PM Integration Routes
# =============================================================================


@router.get(
    "/projects/{project_id}/stats",
    summary="Get document statistics for project",
)
async def get_project_document_stats(
    project_id: UUID,
    service=Depends(get_document_service),
):
    """
    Get document statistics for PM module integration.
    
    Returns counts and summaries for project dashboards.
    """
    documents = await service.list_documents(project_id=project_id)
    
    # Calculate stats
    status_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    total_versions = 0
    
    for doc in documents.items:
        # Count by status
        status_counts[doc.status] = status_counts.get(doc.status, 0) + 1
        
        # Count by type
        type_name = doc.document_type.name if doc.document_type else "Untyped"
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Count versions
        if doc.current_version:
            total_versions += 1
    
    return {
        "project_id": str(project_id),
        "total_documents": documents.total,
        "by_status": status_counts,
        "by_type": type_counts,
        "total_versions": total_versions,
    }


@router.get(
    "/projects/{project_id}/recent",
    summary="Get recently modified documents",
)
async def get_recent_documents(
    project_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    service=Depends(get_document_service),
):
    """
    Get recently modified documents for PM dashboards.
    """
    documents = await service.list_documents(
        project_id=project_id,
        page_size=limit,
    )
    
    return {
        "project_id": str(project_id),
        "documents": documents.items,
    }


# =============================================================================
# Entry Point
# =============================================================================


def load_api_routes() -> APIRouter:
    """
    Entry point for loading API routes.
    Called by serp-shell during module discovery.
    """
    return router
