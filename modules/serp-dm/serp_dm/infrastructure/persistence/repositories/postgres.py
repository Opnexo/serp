"""
PostgreSQL repository implementations for Document Management module.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from serp_dm.domain.entities import (
    ApprovalRequest,
    AuditLogEntry,
    Document,
    DocumentType,
    DocumentVersion,
    Folder,
    Stage,
    StorageTemplate,
    TemplateFolder,
)
from serp_dm.domain.repositories import (
    IApprovalRequestRepository,
    IAuditLogRepository,
    IDocumentRepository,
    IDocumentTypeRepository,
    IDocumentVersionRepository,
    IFolderRepository,
    IStageRepository,
    IStorageTemplateRepository,
    ITemplateFolderRepository,
)
from serp_dm.domain.value_objects import (
    ApprovalStatus,
    DocumentStatus,
    Phase,
    StorageKey,
    Version,
    VersionScheme,
)
from serp_dm.infrastructure.persistence.models import (
    ApprovalRequestModel,
    AuditLogModel,
    DocumentModel,
    DocumentTypeModel,
    DocumentVersionModel,
    FolderModel,
    StageModel,
    StorageTemplateModel,
    TemplateFolderModel,
)


# =============================================================================
# Document Repository
# =============================================================================


class PostgresDocumentRepository(IDocumentRepository):
    """PostgreSQL implementation of Document repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: DocumentModel) -> Document:
        """Convert model to entity."""
        return Document(
            id=model.id,
            project_id=model.project_id,
            title=model.title,
            document_number=model.document_number,
            document_type_id=model.document_type_id,
            folder_id=model.folder_id,
            stage_id=model.stage_id,
            version_scheme=VersionScheme(model.version_scheme),
            current_version=model.current_version,
            status=DocumentStatus(model.status),
            description=model.description,
            tags=model.tags or [],
            metadata=model.metadata_ or {},
            external_references=model.external_references or [],
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_archived=model.is_archived,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Document) -> DocumentModel:
        """Convert entity to model."""
        return DocumentModel(
            id=entity.id,
            project_id=entity.project_id,
            title=entity.title,
            document_number=entity.document_number,
            document_type_id=entity.document_type_id,
            folder_id=entity.folder_id,
            stage_id=entity.stage_id,
            version_scheme=entity.version_scheme.value,
            current_version=entity.current_version,
            status=entity.status.value,
            description=entity.description,
            tags=entity.tags,
            metadata_=entity.metadata,
            external_references=entity.external_references,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            is_archived=entity.is_archived,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[Document]:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_document_number(self, number: str) -> Optional[Document]:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.document_number == number)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_project(
        self,
        project_id: UUID,
        folder_id: Optional[UUID] = None,
        stage_id: Optional[UUID] = None,
        status: Optional[DocumentStatus] = None,
        document_type_id: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Document]:
        query = select(DocumentModel).where(
            and_(
                DocumentModel.project_id == project_id,
                DocumentModel.is_archived == False,
            )
        )

        if folder_id is not None:
            query = query.where(DocumentModel.folder_id == folder_id)
        if stage_id is not None:
            query = query.where(DocumentModel.stage_id == stage_id)
        if status is not None:
            query = query.where(DocumentModel.status == status.value)
        if document_type_id is not None:
            query = query.where(DocumentModel.document_type_id == document_type_id)
        if search:
            query = query.where(
                or_(
                    DocumentModel.title.ilike(f"%{search}%"),
                    DocumentModel.document_number.ilike(f"%{search}%"),
                    DocumentModel.description.ilike(f"%{search}%"),
                )
            )

        query = query.order_by(desc(DocumentModel.updated_at))
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_by_project(
        self,
        project_id: UUID,
        folder_id: Optional[UUID] = None,
        stage_id: Optional[UUID] = None,
        status: Optional[DocumentStatus] = None,
        document_type_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> int:
        query = select(func.count(DocumentModel.id)).where(
            and_(
                DocumentModel.project_id == project_id,
                DocumentModel.is_archived == False,
            )
        )

        if folder_id is not None:
            query = query.where(DocumentModel.folder_id == folder_id)
        if stage_id is not None:
            query = query.where(DocumentModel.stage_id == stage_id)
        if status is not None:
            query = query.where(DocumentModel.status == status.value)
        if document_type_id is not None:
            query = query.where(DocumentModel.document_type_id == document_type_id)
        if search:
            query = query.where(
                or_(
                    DocumentModel.title.ilike(f"%{search}%"),
                    DocumentModel.document_number.ilike(f"%{search}%"),
                )
            )

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_next_sequence(
        self,
        project_id: UUID,
        phase: Phase,
        doc_type_code: str,
    ) -> int:
        # Count existing documents with same project/phase/type prefix
        # Document numbers are like F1234567-001-DRAW-0001-000
        prefix = f"%-{phase.value}-{doc_type_code}-%"
        result = await self.session.execute(
            select(func.count(DocumentModel.id)).where(
                and_(
                    DocumentModel.project_id == project_id,
                    DocumentModel.document_number.ilike(prefix),
                )
            )
        )
        count = result.scalar() or 0
        return count + 1

    async def save(self, document: Document) -> Document:
        if document.id == UUID(int=0):
            document.id = uuid4()
        model = self._to_model(document)
        await self.session.merge(model)
        await self.session.commit()
        return document

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_archived = True
            await self.session.commit()


# =============================================================================
# Document Version Repository
# =============================================================================


class PostgresDocumentVersionRepository(IDocumentVersionRepository):
    """PostgreSQL implementation of DocumentVersion repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: DocumentVersionModel) -> DocumentVersion:
        return DocumentVersion(
            id=model.id,
            document_id=model.document_id,
            version=Version(
                scheme=VersionScheme.SEMANTIC,  # Determined from version_string
                major=model.major,
                minor=model.minor,
                patch=model.patch,
                sequence=model.sequence,
            ),
            storage_key=StorageKey(key=model.storage_key),
            original_filename=model.original_filename,
            generated_filename=model.generated_filename,
            mime_type=model.mime_type,
            size_bytes=model.size_bytes,
            checksum=model.checksum,
            change_note=model.change_note,
            uploaded_by=model.uploaded_by,
            uploaded_at=model.created_at,
            created_at=model.created_at,
        )

    def _to_model(self, entity: DocumentVersion) -> DocumentVersionModel:
        return DocumentVersionModel(
            id=entity.id,
            document_id=entity.document_id,
            version_string=str(entity.version),
            major=entity.version.major,
            minor=entity.version.minor,
            patch=entity.version.patch,
            sequence=entity.version.sequence,
            storage_key=entity.storage_key.key,
            original_filename=entity.original_filename,
            generated_filename=entity.generated_filename,
            mime_type=entity.mime_type,
            size_bytes=entity.size_bytes,
            checksum=entity.checksum,
            change_note=entity.change_note,
            uploaded_by=entity.uploaded_by,
            created_at=entity.uploaded_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersionModel).where(DocumentVersionModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_latest(self, document_id: UUID) -> Optional[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersionModel)
            .where(DocumentVersionModel.document_id == document_id)
            .order_by(desc(DocumentVersionModel.created_at))
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_document(
        self,
        document_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersionModel)
            .where(DocumentVersionModel.document_id == document_id)
            .order_by(desc(DocumentVersionModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_by_document(self, document_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(DocumentVersionModel.id)).where(
                DocumentVersionModel.document_id == document_id
            )
        )
        return result.scalar() or 0

    async def save(self, version: DocumentVersion) -> DocumentVersion:
        if version.id == UUID(int=0):
            version.id = uuid4()
        model = self._to_model(version)
        self.session.add(model)
        await self.session.commit()
        return version


# =============================================================================
# Stage Repository
# =============================================================================


class PostgresStageRepository(IStageRepository):
    """PostgreSQL implementation of Stage repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: StageModel) -> Stage:
        return Stage(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            description=model.description,
            order=model.order_index,
            color=model.color,
            is_default=model.is_default,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Stage) -> StageModel:
        return StageModel(
            id=entity.id,
            project_id=entity.project_id,
            name=entity.name,
            description=entity.description,
            order_index=entity.order,
            color=entity.color,
            is_default=entity.is_default,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[Stage]:
        result = await self.session.execute(
            select(StageModel).where(StageModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_default(self, project_id: UUID) -> Optional[Stage]:
        result = await self.session.execute(
            select(StageModel).where(
                and_(StageModel.project_id == project_id, StageModel.is_default == True)
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_project(self, project_id: UUID) -> list[Stage]:
        result = await self.session.execute(
            select(StageModel)
            .where(and_(StageModel.project_id == project_id, StageModel.is_active == True))
            .order_by(StageModel.order_index)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, stage: Stage) -> Stage:
        if stage.id == UUID(int=0):
            stage.id = uuid4()
        model = self._to_model(stage)
        await self.session.merge(model)
        await self.session.commit()
        return stage

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(StageModel).where(StageModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_active = False
            await self.session.commit()

    async def reorder(self, project_id: UUID, stage_ids: list[UUID]) -> None:
        for index, stage_id in enumerate(stage_ids):
            result = await self.session.execute(
                select(StageModel).where(StageModel.id == stage_id)
            )
            model = result.scalar_one_or_none()
            if model and model.project_id == project_id:
                model.order_index = index
        await self.session.commit()


# =============================================================================
# Folder Repository
# =============================================================================


class PostgresFolderRepository(IFolderRepository):
    """PostgreSQL implementation of Folder repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: FolderModel) -> Folder:
        return Folder(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            path=model.path,
            parent_id=model.parent_id,
            description=model.description,
            is_archived=model.is_archived,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Folder) -> FolderModel:
        return FolderModel(
            id=entity.id,
            project_id=entity.project_id,
            name=entity.name,
            path=entity.path,
            parent_id=entity.parent_id,
            description=entity.description,
            is_archived=entity.is_archived,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[Folder]:
        result = await self.session.execute(
            select(FolderModel).where(FolderModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_path(self, project_id: UUID, path: str) -> Optional[Folder]:
        result = await self.session.execute(
            select(FolderModel).where(
                and_(FolderModel.project_id == project_id, FolderModel.path == path)
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_project(
        self,
        project_id: UUID,
        parent_id: Optional[UUID] = None,
    ) -> list[Folder]:
        query = select(FolderModel).where(
            and_(FolderModel.project_id == project_id, FolderModel.is_archived == False)
        )
        if parent_id is not None:
            query = query.where(FolderModel.parent_id == parent_id)
        else:
            query = query.where(FolderModel.parent_id.is_(None))

        result = await self.session.execute(query.order_by(FolderModel.name))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, folder: Folder) -> Folder:
        if folder.id == UUID(int=0):
            folder.id = uuid4()
        model = self._to_model(folder)
        await self.session.merge(model)
        await self.session.commit()
        return folder

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(FolderModel).where(FolderModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_archived = True
            await self.session.commit()


# =============================================================================
# Storage Template Repository
# =============================================================================


class PostgresStorageTemplateRepository(IStorageTemplateRepository):
    """PostgreSQL implementation of StorageTemplate repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: StorageTemplateModel) -> StorageTemplate:
        return StorageTemplate(
            id=model.id,
            name=model.name,
            description=model.description,
            is_default=model.is_default,
            is_active=model.is_active,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: StorageTemplate) -> StorageTemplateModel:
        return StorageTemplateModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_default=entity.is_default,
            is_active=entity.is_active,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[StorageTemplate]:
        result = await self.session.execute(
            select(StorageTemplateModel).where(StorageTemplateModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_default(self) -> Optional[StorageTemplate]:
        result = await self.session.execute(
            select(StorageTemplateModel).where(StorageTemplateModel.is_default == True)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, include_inactive: bool = False) -> list[StorageTemplate]:
        query = select(StorageTemplateModel)
        if not include_inactive:
            query = query.where(StorageTemplateModel.is_active == True)
        result = await self.session.execute(query.order_by(StorageTemplateModel.name))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, template: StorageTemplate) -> StorageTemplate:
        if template.id == UUID(int=0):
            template.id = uuid4()
        model = self._to_model(template)
        await self.session.merge(model)
        await self.session.commit()
        return template

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(StorageTemplateModel).where(StorageTemplateModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_active = False
            await self.session.commit()


# =============================================================================
# Template Folder Repository
# =============================================================================


class PostgresTemplateFolderRepository(ITemplateFolderRepository):
    """PostgreSQL implementation of TemplateFolder repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: TemplateFolderModel) -> TemplateFolder:
        return TemplateFolder(
            id=model.id,
            template_id=model.template_id,
            name=model.name,
            path=model.path,
            parent_id=model.parent_id,
            description=model.description,
            order=model.order_index,
            created_at=model.created_at,
        )

    def _to_model(self, entity: TemplateFolder) -> TemplateFolderModel:
        return TemplateFolderModel(
            id=entity.id,
            template_id=entity.template_id,
            name=entity.name,
            path=entity.path,
            parent_id=entity.parent_id,
            description=entity.description,
            order_index=entity.order,
            created_at=entity.created_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[TemplateFolder]:
        result = await self.session.execute(
            select(TemplateFolderModel).where(TemplateFolderModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_template(self, template_id: UUID) -> list[TemplateFolder]:
        result = await self.session.execute(
            select(TemplateFolderModel)
            .where(TemplateFolderModel.template_id == template_id)
            .order_by(TemplateFolderModel.order_index)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, folder: TemplateFolder) -> TemplateFolder:
        if folder.id == UUID(int=0):
            folder.id = uuid4()
        model = self._to_model(folder)
        await self.session.merge(model)
        await self.session.commit()
        return folder

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(TemplateFolderModel).where(TemplateFolderModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()


# =============================================================================
# Document Type Repository
# =============================================================================


class PostgresDocumentTypeRepository(IDocumentTypeRepository):
    """PostgreSQL implementation of DocumentType repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: DocumentTypeModel) -> DocumentType:
        return DocumentType(
            id=model.id,
            code=model.code,
            name=model.name,
            description=model.description,
            category=model.category,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: DocumentType) -> DocumentTypeModel:
        return DocumentTypeModel(
            id=entity.id,
            code=entity.code,
            name=entity.name,
            description=entity.description,
            category=entity.category,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[DocumentType]:
        result = await self.session.execute(
            select(DocumentTypeModel).where(DocumentTypeModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_code(self, code: str) -> Optional[DocumentType]:
        result = await self.session.execute(
            select(DocumentTypeModel).where(DocumentTypeModel.code == code)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(
        self,
        category: Optional[str] = None,
        include_inactive: bool = False,
    ) -> list[DocumentType]:
        query = select(DocumentTypeModel)
        if not include_inactive:
            query = query.where(DocumentTypeModel.is_active == True)
        if category:
            query = query.where(DocumentTypeModel.category == category)
        result = await self.session.execute(query.order_by(DocumentTypeModel.code))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, doc_type: DocumentType) -> DocumentType:
        if doc_type.id == UUID(int=0):
            doc_type.id = uuid4()
        model = self._to_model(doc_type)
        await self.session.merge(model)
        await self.session.commit()
        return doc_type

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(DocumentTypeModel).where(DocumentTypeModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_active = False
            await self.session.commit()


# =============================================================================
# Approval Request Repository
# =============================================================================


class PostgresApprovalRequestRepository(IApprovalRequestRepository):
    """PostgreSQL implementation of ApprovalRequest repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ApprovalRequestModel) -> ApprovalRequest:
        return ApprovalRequest(
            id=model.id,
            document_id=model.document_id,
            version_string=model.version_string,
            requested_by=model.requested_by,
            assigned_to=model.assigned_to,
            status=ApprovalStatus(model.status),
            request_note=model.request_note,
            decision_note=model.decision_note,
            requested_at=model.requested_at,
            decided_at=model.decided_at,
            created_at=model.requested_at,
        )

    def _to_model(self, entity: ApprovalRequest) -> ApprovalRequestModel:
        return ApprovalRequestModel(
            id=entity.id,
            document_id=entity.document_id,
            version_string=entity.version_string,
            requested_by=entity.requested_by,
            assigned_to=entity.assigned_to,
            status=entity.status.value,
            request_note=entity.request_note,
            decision_note=entity.decision_note,
            requested_at=entity.requested_at,
            decided_at=entity.decided_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[ApprovalRequest]:
        result = await self.session.execute(
            select(ApprovalRequestModel).where(ApprovalRequestModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_document(self, document_id: UUID) -> list[ApprovalRequest]:
        result = await self.session.execute(
            select(ApprovalRequestModel)
            .where(ApprovalRequestModel.document_id == document_id)
            .order_by(desc(ApprovalRequestModel.requested_at))
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_pending_for_user(self, user_id: UUID) -> list[ApprovalRequest]:
        result = await self.session.execute(
            select(ApprovalRequestModel).where(
                and_(
                    ApprovalRequestModel.assigned_to == user_id,
                    ApprovalRequestModel.status == ApprovalStatus.PENDING.value,
                )
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_status(
        self,
        status: ApprovalStatus,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ApprovalRequest]:
        result = await self.session.execute(
            select(ApprovalRequestModel)
            .where(ApprovalRequestModel.status == status.value)
            .order_by(desc(ApprovalRequestModel.requested_at))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, request: ApprovalRequest) -> ApprovalRequest:
        if request.id == UUID(int=0):
            request.id = uuid4()
        model = self._to_model(request)
        await self.session.merge(model)
        await self.session.commit()
        return request


# =============================================================================
# Audit Log Repository (Append-only)
# =============================================================================


class PostgresAuditLogRepository(IAuditLogRepository):
    """PostgreSQL implementation of AuditLog repository (append-only)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: AuditLogModel) -> AuditLogEntry:
        return AuditLogEntry(
            id=model.id,
            action=model.action,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            user_id=model.user_id,
            timestamp=model.timestamp,
            details=model.details or {},
            ip_address=model.ip_address,
        )

    async def log(self, entry: AuditLogEntry) -> AuditLogEntry:
        if entry.id == UUID(int=0):
            entry.id = uuid4()
        model = AuditLogModel(
            id=entry.id,
            action=entry.action,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            user_id=entry.user_id,
            timestamp=entry.timestamp,
            details=entry.details,
            ip_address=entry.ip_address,
        )
        self.session.add(model)
        await self.session.commit()
        return entry

    async def list_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        result = await self.session.execute(
            select(AuditLogModel)
            .where(
                and_(
                    AuditLogModel.entity_type == entity_type,
                    AuditLogModel.entity_id == entity_id,
                )
            )
            .order_by(desc(AuditLogModel.timestamp))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        result = await self.session.execute(
            select(AuditLogModel)
            .where(AuditLogModel.user_id == user_id)
            .order_by(desc(AuditLogModel.timestamp))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def search(
        self,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        user_id: Optional[UUID] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        query = select(AuditLogModel)

        if action:
            query = query.where(AuditLogModel.action == action)
        if entity_type:
            query = query.where(AuditLogModel.entity_type == entity_type)
        if user_id:
            query = query.where(AuditLogModel.user_id == user_id)
        if from_date:
            query = query.where(AuditLogModel.timestamp >= datetime.fromisoformat(from_date))
        if to_date:
            query = query.where(AuditLogModel.timestamp <= datetime.fromisoformat(to_date))

        result = await self.session.execute(
            query.order_by(desc(AuditLogModel.timestamp)).offset(skip).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]
