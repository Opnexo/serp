"""
FastAPI routes for Document Management module.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from serp_core.auth.decorators import require_permission

from serp_dm.application.dto import (
    CreateDocumentRequest,
    CreateFolderRequest,
    DocumentDTO,
    DocumentListResponse,
    FolderDTO,
    FolderListResponse,
    UpdateDocumentRequest,
    UpdateFolderRequest,
)
from serp_dm.application.services import DocumentService, FolderService
from serp_dm.infrastructure.persistence.repositories.memory import (
    InMemoryDocumentRepository,
    InMemoryFolderRepository,
)

router = APIRouter()


# Dependency injection (simplified - in production, use proper DI container)
def get_document_service() -> DocumentService:
    """Get document service instance."""
    return DocumentService(InMemoryDocumentRepository())


def get_folder_service() -> FolderService:
    """Get folder service instance."""
    return FolderService(InMemoryFolderRepository())


# Document routes
@router.get("/documents", response_model=DocumentListResponse)
# @require_permission("dm.document.list")
async def list_documents(
    folder_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 50,
    service: DocumentService = Depends(get_document_service),
):
    """List all documents."""
    documents = await service.list_documents(folder_id=folder_id, page=page, page_size=page_size)
    return DocumentListResponse(
        items=documents,
        total=len(documents),
        page=page,
        page_size=page_size,
    )


@router.get("/documents/{document_id}", response_model=DocumentDTO)
# @require_permission("dm.document.read")
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    """Get document by ID."""
    document = await service.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.post("/documents", response_model=DocumentDTO, status_code=status.HTTP_201_CREATED)
# @require_permission("dm.document.create")
async def create_document(
    request: CreateDocumentRequest,
    service: DocumentService = Depends(get_document_service),
):
    """Create a new document."""
    return await service.create_document(request)


@router.put("/documents/{document_id}", response_model=DocumentDTO)
# @require_permission("dm.document.update")
async def update_document(
    document_id: UUID,
    request: UpdateDocumentRequest,
    service: DocumentService = Depends(get_document_service),
):
    """Update document."""
    document = await service.update_document(document_id, request)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
# @require_permission("dm.document.delete")
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    """Delete document."""
    success = await service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )


# Folder routes
@router.get("/folders", response_model=FolderListResponse)
# @require_permission("dm.folder.list")
async def list_folders(
    parent_id: Optional[UUID] = None,
    service: FolderService = Depends(get_folder_service),
):
    """List all folders."""
    folders = await service.list_folders(parent_id=parent_id)
    return FolderListResponse(
        items=folders,
        total=len(folders),
    )


@router.get("/folders/{folder_id}", response_model=FolderDTO)
# @require_permission("dm.folder.read")
async def get_folder(
    folder_id: UUID,
    service: FolderService = Depends(get_folder_service),
):
    """Get folder by ID."""
    folder = await service.get_folder(folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )
    return folder


@router.post("/folders", response_model=FolderDTO, status_code=status.HTTP_201_CREATED)
# @require_permission("dm.folder.create")
async def create_folder(
    request: CreateFolderRequest,
    service: FolderService = Depends(get_folder_service),
):
    """Create a new folder."""
    return await service.create_folder(request)


def load_api_routes() -> APIRouter:
    """
    Entry point for loading API routes.
    Called by serp-shell during module discovery.
    """
    return router
