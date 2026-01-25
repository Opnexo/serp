"""
In-memory repository implementations for testing.
"""

from typing import Optional
from uuid import UUID, uuid4

from serp_dm.domain.entities import Document, DocumentVersion, Folder
from serp_dm.domain.repositories import (
    IDocumentRepository,
    IDocumentVersionRepository,
    IFolderRepository,
)


class InMemoryDocumentRepository(IDocumentRepository):
    """In-memory document repository for testing."""

    def __init__(self):
        self._documents: dict[UUID, Document] = {}

    async def get_by_id(self, id: UUID) -> Optional[Document]:
        return self._documents.get(id)

    async def save(self, entity: Document) -> Document:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        self._documents[entity.id] = entity
        return entity

    async def delete(self, id: UUID) -> None:
        self._documents.pop(id, None)

    async def list_all(self) -> list[Document]:
        return list(self._documents.values())

    async def find_by_name(self, name: str) -> Optional[Document]:
        for doc in self._documents.values():
            if doc.name == name:
                return doc
        return None

    async def find_by_folder(self, folder_id: UUID) -> list[Document]:
        return [doc for doc in self._documents.values() if doc.folder_id == folder_id]

    async def find_by_tags(self, tags: list[str]) -> list[Document]:
        return [
            doc
            for doc in self._documents.values()
            if any(tag in doc.tags for tag in tags)
        ]

    async def search(self, query: str) -> list[Document]:
        query_lower = query.lower()
        return [
            doc
            for doc in self._documents.values()
            if query_lower in doc.name.lower() or query_lower in doc.description.lower()
        ]


class InMemoryFolderRepository(IFolderRepository):
    """In-memory folder repository for testing."""

    def __init__(self):
        self._folders: dict[UUID, Folder] = {}

    async def get_by_id(self, id: UUID) -> Optional[Folder]:
        return self._folders.get(id)

    async def save(self, entity: Folder) -> Folder:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        self._folders[entity.id] = entity
        return entity

    async def delete(self, id: UUID) -> None:
        self._folders.pop(id, None)

    async def list_all(self) -> list[Folder]:
        return list(self._folders.values())

    async def find_by_name(
        self, name: str, parent_id: Optional[UUID] = None
    ) -> Optional[Folder]:
        for folder in self._folders.values():
            if folder.name == name and folder.parent_id == parent_id:
                return folder
        return None

    async def find_by_parent(self, parent_id: Optional[UUID]) -> list[Folder]:
        return [
            folder
            for folder in self._folders.values()
            if folder.parent_id == parent_id
        ]

    async def get_folder_path(self, folder_id: UUID) -> str:
        folder = self._folders.get(folder_id)
        return folder.path if folder else "/"


class InMemoryDocumentVersionRepository(IDocumentVersionRepository):
    """In-memory document version repository for testing."""

    def __init__(self):
        self._versions: dict[UUID, DocumentVersion] = {}

    async def get_by_id(self, id: UUID) -> Optional[DocumentVersion]:
        return self._versions.get(id)

    async def save(self, entity: DocumentVersion) -> DocumentVersion:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        self._versions[entity.id] = entity
        return entity

    async def delete(self, id: UUID) -> None:
        self._versions.pop(id, None)

    async def list_all(self) -> list[DocumentVersion]:
        return list(self._versions.values())

    async def find_by_document(self, document_id: UUID) -> list[DocumentVersion]:
        return [
            ver for ver in self._versions.values() if ver.document_id == document_id
        ]

    async def find_by_version_number(
        self, document_id: UUID, version_number: int
    ) -> Optional[DocumentVersion]:
        for ver in self._versions.values():
            if ver.document_id == document_id and ver.version_number == version_number:
                return ver
        return None

    async def get_latest_version(
        self, document_id: UUID
    ) -> Optional[DocumentVersion]:
        versions = await self.find_by_document(document_id)
        if not versions:
            return None
        return max(versions, key=lambda v: v.version_number)
