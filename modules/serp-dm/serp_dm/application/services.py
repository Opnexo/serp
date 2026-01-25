"""
Application services for Document Management module.
"""

from typing import Optional
from uuid import UUID

from serp_core.application.service import ApplicationService

from serp_dm.application.dto import (
    CreateDocumentRequest,
    CreateFolderRequest,
    DocumentDTO,
    FolderDTO,
    UpdateDocumentRequest,
    UpdateFolderRequest,
)
from serp_dm.domain.entities import Document, Folder
from serp_dm.domain.repositories import IDocumentRepository, IFolderRepository


class DocumentService(ApplicationService):
    """
    Application service for document management.
    """

    def __init__(
        self,
        document_repository: IDocumentRepository,
    ):
        self.document_repository = document_repository

    async def create_document(
        self, request: CreateDocumentRequest, created_by: Optional[UUID] = None
    ) -> DocumentDTO:
        """
        Create a new document.

        Args:
            request: Document creation request
            created_by: User ID creating the document

        Returns:
            Created document DTO
        """
        document = Document(
            id=UUID(int=0),  # Will be set by repository
            name=request.name,
            folder_id=request.folder_id,
            file_path=request.file_path,
            mime_type=request.mime_type,
            size_bytes=request.size_bytes,
            checksum=request.checksum,
            description=request.description,
            tags=request.tags,
            metadata=request.metadata,
            created_by=created_by,
            updated_by=created_by,
        )

        saved_document = await self.document_repository.save(document)
        return self._to_dto(saved_document)

    async def get_document(self, document_id: UUID) -> Optional[DocumentDTO]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document DTO or None if not found
        """
        document = await self.document_repository.get_by_id(document_id)
        return self._to_dto(document) if document else None

    async def update_document(
        self,
        document_id: UUID,
        request: UpdateDocumentRequest,
        updated_by: Optional[UUID] = None,
    ) -> Optional[DocumentDTO]:
        """
        Update document.

        Args:
            document_id: Document ID
            request: Update request
            updated_by: User ID updating the document

        Returns:
            Updated document DTO or None if not found
        """
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            return None

        if request.name is not None:
            document.name = request.name
        if request.folder_id is not None:
            document.folder_id = request.folder_id
        if request.description is not None:
            document.description = request.description
        if request.tags is not None:
            document.tags = request.tags
        if request.metadata is not None:
            document.update_metadata(request.metadata)

        document.updated_by = updated_by

        updated_document = await self.document_repository.save(document)
        return self._to_dto(updated_document)

    async def delete_document(self, document_id: UUID) -> bool:
        """
        Delete document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            return False

        await self.document_repository.delete(document_id)
        return True

    async def list_documents(
        self, folder_id: Optional[UUID] = None, page: int = 1, page_size: int = 50
    ) -> list[DocumentDTO]:
        """
        List documents, optionally filtered by folder.

        Args:
            folder_id: Optional folder ID to filter by
            page: Page number
            page_size: Items per page

        Returns:
            List of document DTOs
        """
        if folder_id:
            documents = await self.document_repository.find_by_folder(folder_id)
        else:
            documents = await self.document_repository.list_all()

        return [self._to_dto(doc) for doc in documents]

    def _to_dto(self, document: Document) -> DocumentDTO:
        """Convert domain entity to DTO."""
        return DocumentDTO(
            id=document.id,
            name=document.name,
            folder_id=document.folder_id,
            file_path=document.file_path,
            mime_type=document.mime_type,
            size_bytes=document.size_bytes,
            checksum=document.checksum,
            version=document.version,
            description=document.description,
            tags=document.tags,
            metadata=document.metadata,
            created_by=document.created_by,
            updated_by=document.updated_by,
            is_archived=document.is_archived,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class FolderService(ApplicationService):
    """
    Application service for folder management.
    """

    def __init__(self, folder_repository: IFolderRepository):
        self.folder_repository = folder_repository

    async def create_folder(
        self, request: CreateFolderRequest, created_by: Optional[UUID] = None
    ) -> FolderDTO:
        """
        Create a new folder.

        Args:
            request: Folder creation request
            created_by: User ID creating the folder

        Returns:
            Created folder DTO
        """
        # Build path
        path = "/"
        if request.parent_id:
            parent = await self.folder_repository.get_by_id(request.parent_id)
            if parent:
                path = f"{parent.path}/{request.name}" if parent.path != "/" else f"/{request.name}"

        folder = Folder(
            id=UUID(int=0),  # Will be set by repository
            name=request.name,
            parent_id=request.parent_id,
            description=request.description,
            path=path,
            created_by=created_by,
        )

        saved_folder = await self.folder_repository.save(folder)
        return self._to_dto(saved_folder)

    async def get_folder(self, folder_id: UUID) -> Optional[FolderDTO]:
        """Get folder by ID."""
        folder = await self.folder_repository.get_by_id(folder_id)
        return self._to_dto(folder) if folder else None

    async def list_folders(
        self, parent_id: Optional[UUID] = None
    ) -> list[FolderDTO]:
        """List folders under a parent."""
        folders = await self.folder_repository.find_by_parent(parent_id)
        return [self._to_dto(folder) for folder in folders]

    def _to_dto(self, folder: Folder) -> FolderDTO:
        """Convert domain entity to DTO."""
        return FolderDTO(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            description=folder.description,
            path=folder.path,
            created_by=folder.created_by,
            is_archived=folder.is_archived,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
        )
