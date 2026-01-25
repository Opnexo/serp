"""
PostgreSQL repository implementations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from serp_dm.domain.entities import Document, DocumentVersion, Folder
from serp_dm.domain.repositories import (
    IDocumentRepository,
    IDocumentVersionRepository,
    IFolderRepository,
)
from serp_dm.infrastructure.persistence.models import (
    DocumentModel,
    DocumentVersionModel,
    FolderModel,
)


class PostgresDocumentRepository(IDocumentRepository):
    """PostgreSQL document repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[Document]:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: Document) -> Document:
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)

    async def list_all(self) -> list[Document]:
        result = await self.session.execute(select(DocumentModel))
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_name(self, name: str) -> Optional[Document]:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.name == name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_folder(self, folder_id: UUID) -> list[Document]:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.folder_id == folder_id)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_tags(self, tags: list[str]) -> list[Document]:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.tags.overlap(tags))
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def search(self, query: str) -> list[Document]:
        result = await self.session.execute(
            select(DocumentModel).where(
                DocumentModel.name.ilike(f"%{query}%")
                | DocumentModel.description.ilike(f"%{query}%")
            )
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: DocumentModel) -> Document:
        """Convert model to entity."""
        return Document(
            id=model.id,
            name=model.name,
            folder_id=model.folder_id,
            file_path=model.file_path,
            mime_type=model.mime_type,
            size_bytes=model.size_bytes,
            checksum=model.checksum,
            version=model.version,
            description=model.description,
            tags=model.tags or [],
            metadata=model.metadata or {},
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_archived=model.is_archived,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Document) -> DocumentModel:
        """Convert entity to model."""
        return DocumentModel(
            id=entity.id if entity.id != UUID(int=0) else None,
            name=entity.name,
            folder_id=entity.folder_id,
            file_path=entity.file_path,
            mime_type=entity.mime_type,
            size_bytes=entity.size_bytes,
            checksum=entity.checksum,
            version=entity.version,
            description=entity.description,
            tags=entity.tags,
            metadata=entity.metadata,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            is_archived=entity.is_archived,
        )


class PostgresFolderRepository(IFolderRepository):
    """PostgreSQL folder repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[Folder]:
        result = await self.session.execute(
            select(FolderModel).where(FolderModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: Folder) -> Folder:
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(FolderModel).where(FolderModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)

    async def list_all(self) -> list[Folder]:
        result = await self.session.execute(select(FolderModel))
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_name(
        self, name: str, parent_id: Optional[UUID] = None
    ) -> Optional[Folder]:
        result = await self.session.execute(
            select(FolderModel).where(
                FolderModel.name == name, FolderModel.parent_id == parent_id
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_parent(self, parent_id: Optional[UUID]) -> list[Folder]:
        result = await self.session.execute(
            select(FolderModel).where(FolderModel.parent_id == parent_id)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_folder_path(self, folder_id: UUID) -> str:
        folder = await self.get_by_id(folder_id)
        return folder.path if folder else "/"

    def _to_entity(self, model: FolderModel) -> Folder:
        """Convert model to entity."""
        return Folder(
            id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            description=model.description,
            path=model.path,
            created_by=model.created_by,
            is_archived=model.is_archived,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Folder) -> FolderModel:
        """Convert entity to model."""
        return FolderModel(
            id=entity.id if entity.id != UUID(int=0) else None,
            name=entity.name,
            parent_id=entity.parent_id,
            description=entity.description,
            path=entity.path,
            created_by=entity.created_by,
            is_archived=entity.is_archived,
        )


class PostgresDocumentVersionRepository(IDocumentVersionRepository):
    """PostgreSQL document version repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersionModel).where(DocumentVersionModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: DocumentVersion) -> DocumentVersion:
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(DocumentVersionModel).where(DocumentVersionModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)

    async def list_all(self) -> list[DocumentVersion]:
        result = await self.session.execute(select(DocumentVersionModel))
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_document(self, document_id: UUID) -> list[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersionModel).where(
                DocumentVersionModel.document_id == document_id
            )
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_version_number(
        self, document_id: UUID, version_number: int
    ) -> Optional[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersionModel).where(
                DocumentVersionModel.document_id == document_id,
                DocumentVersionModel.version_number == version_number,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_latest_version(
        self, document_id: UUID
    ) -> Optional[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersionModel)
            .where(DocumentVersionModel.document_id == document_id)
            .order_by(DocumentVersionModel.version_number.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_entity(self, model: DocumentVersionModel) -> DocumentVersion:
        """Convert model to entity."""
        return DocumentVersion(
            id=model.id,
            document_id=model.document_id,
            version_number=model.version_number,
            file_path=model.file_path,
            size_bytes=model.size_bytes,
            checksum=model.checksum,
            created_by=model.created_by,
            change_note=model.change_note,
            metadata=model.metadata or {},
            created_at=model.created_at,
        )

    def _to_model(self, entity: DocumentVersion) -> DocumentVersionModel:
        """Convert entity to model."""
        return DocumentVersionModel(
            id=entity.id if entity.id != UUID(int=0) else None,
            document_id=entity.document_id,
            version_number=entity.version_number,
            file_path=entity.file_path,
            size_bytes=entity.size_bytes,
            checksum=entity.checksum,
            created_by=entity.created_by,
            change_note=entity.change_note,
            metadata=entity.metadata,
        )
