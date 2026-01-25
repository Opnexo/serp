"""
Repository interfaces for Document Management module.
"""

from abc import abstractmethod
from typing import Optional
from uuid import UUID

from serp_core.domain.repository import IRepository

from serp_dm.domain.entities import Document, DocumentVersion, Folder


class IDocumentRepository(IRepository[Document]):
    """
    Document repository interface.
    """

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Document]:
        """Find document by name."""
        pass

    @abstractmethod
    async def find_by_folder(self, folder_id: UUID) -> list[Document]:
        """Find all documents in a folder."""
        pass

    @abstractmethod
    async def find_by_tags(self, tags: list[str]) -> list[Document]:
        """Find documents by tags."""
        pass

    @abstractmethod
    async def search(self, query: str) -> list[Document]:
        """Search documents by name or content."""
        pass


class IFolderRepository(IRepository[Folder]):
    """
    Folder repository interface.
    """

    @abstractmethod
    async def find_by_name(self, name: str, parent_id: Optional[UUID] = None) -> Optional[Folder]:
        """Find folder by name and optional parent."""
        pass

    @abstractmethod
    async def find_by_parent(self, parent_id: Optional[UUID]) -> list[Folder]:
        """Find all folders under a parent."""
        pass

    @abstractmethod
    async def get_folder_path(self, folder_id: UUID) -> str:
        """Get full path of a folder."""
        pass


class IDocumentVersionRepository(IRepository[DocumentVersion]):
    """
    Document version repository interface.
    """

    @abstractmethod
    async def find_by_document(self, document_id: UUID) -> list[DocumentVersion]:
        """Find all versions of a document."""
        pass

    @abstractmethod
    async def find_by_version_number(
        self, document_id: UUID, version_number: int
    ) -> Optional[DocumentVersion]:
        """Find specific version of a document."""
        pass

    @abstractmethod
    async def get_latest_version(self, document_id: UUID) -> Optional[DocumentVersion]:
        """Get the latest version of a document."""
        pass
