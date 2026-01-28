"""
Application services for Document Management module.
"""

import hashlib
from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from serp_core.application.service import ApplicationService

from serp_dm.application.dto import (
    ApprovalDecisionRequest,
    ApprovalRequestDTO,
    CreateDocumentTypeRequest,
    CreateFolderRequest,
    CreateStageRequest,
    CreateStorageTemplateRequest,
    DocumentDTO,
    DocumentListResponse,
    DocumentTypeDTO,
    DocumentVersionDTO,
    FolderDTO,
    KanbanBoardResponse,
    MoveDocumentRequest,
    RegisterDocumentRequest,
    StageDTO,
    StorageTemplateDTO,
    SubmitForApprovalRequest,
    UpdateDocumentRequest,
    UpdateDocumentTypeRequest,
    UpdateStageRequest,
    UploadVersionRequest,
)
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
from serp_dm.domain.ports import IDocumentStorage
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
    FileNamingPattern,
    Phase,
    StorageKey,
    Version,
    VersionScheme,
)


class DocumentService(ApplicationService):
    """Application service for document management."""

    def __init__(
        self,
        document_repo: IDocumentRepository,
        version_repo: IDocumentVersionRepository,
        stage_repo: IStageRepository,
        folder_repo: IFolderRepository,
        doc_type_repo: IDocumentTypeRepository,
        storage: IDocumentStorage,
        audit_repo: IAuditLogRepository,
    ):
        self.document_repo = document_repo
        self.version_repo = version_repo
        self.stage_repo = stage_repo
        self.folder_repo = folder_repo
        self.doc_type_repo = doc_type_repo
        self.storage = storage
        self.audit_repo = audit_repo

    async def register_document(
        self,
        request: RegisterDocumentRequest,
        user_id: UUID,
    ) -> DocumentDTO:
        """Register a new document in the system."""
        # Get default stage if not provided
        stage_id = request.stage_id
        if not stage_id:
            default_stage = await self.stage_repo.get_default(request.project_id)
            if default_stage:
                stage_id = default_stage.id

        document = Document(
            id=UUID(int=0),
            project_id=request.project_id,
            title=request.title,
            document_type_id=request.document_type_id,
            folder_id=request.folder_id,
            stage_id=stage_id,
            description=request.description,
            tags=request.tags,
            metadata=request.metadata,
            external_references=request.external_references,
            created_by=user_id,
            updated_by=user_id,
        )

        saved = await self.document_repo.save(document)

        # Audit log
        await self._log_action("document.registered", "document", saved.id, user_id, {
            "title": saved.title,
            "project_id": str(saved.project_id),
        })

        return await self._to_dto(saved)

    async def get_document(self, document_id: UUID) -> Optional[DocumentDTO]:
        """Get document by ID."""
        document = await self.document_repo.get_by_id(document_id)
        return await self._to_dto(document) if document else None

    async def update_document(
        self,
        document_id: UUID,
        request: UpdateDocumentRequest,
        user_id: UUID,
    ) -> Optional[DocumentDTO]:
        """Update document metadata."""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            return None

        if request.title is not None:
            document.title = request.title
        if request.folder_id is not None:
            document.folder_id = request.folder_id
        if request.stage_id is not None:
            document.stage_id = request.stage_id
        if request.description is not None:
            document.description = request.description
        if request.tags is not None:
            document.tags = request.tags
        if request.metadata is not None:
            document.metadata = request.metadata
        if request.external_references is not None:
            document.external_references = request.external_references

        document.updated_by = user_id
        saved = await self.document_repo.save(document)

        await self._log_action("document.updated", "document", saved.id, user_id, {})
        return await self._to_dto(saved)

    async def delete_document(self, document_id: UUID, user_id: UUID) -> bool:
        """Archive a document (soft delete)."""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            return False

        await self.document_repo.delete(document_id)

        await self._log_action("document.archived", "document", document_id, user_id, {})
        return True

    async def list_documents(
        self,
        project_id: UUID,
        folder_id: Optional[UUID] = None,
        stage_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> DocumentListResponse:
        """List documents with filters."""
        skip = (page - 1) * page_size
        status_enum = DocumentStatus(status) if status else None

        documents = await self.document_repo.list_by_project(
            project_id=project_id,
            folder_id=folder_id,
            stage_id=stage_id,
            status=status_enum,
            search=search,
            skip=skip,
            limit=page_size,
        )
        total = await self.document_repo.count_by_project(
            project_id=project_id,
            folder_id=folder_id,
            stage_id=stage_id,
            status=status_enum,
            search=search,
        )

        items = [await self._to_dto(doc) for doc in documents]

        return DocumentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(skip + len(items)) < total,
        )

    async def move_document(
        self,
        document_id: UUID,
        request: MoveDocumentRequest,
        user_id: UUID,
    ) -> Optional[DocumentDTO]:
        """Move document to different stage or folder."""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            return None

        old_stage_id = document.stage_id

        if request.stage_id is not None:
            document.stage_id = request.stage_id
        if request.folder_id is not None:
            document.folder_id = request.folder_id

        document.updated_by = user_id
        saved = await self.document_repo.save(document)

        if request.stage_id and request.stage_id != old_stage_id:
            await self._log_action("document.stage_changed", "document", saved.id, user_id, {
                "old_stage_id": str(old_stage_id) if old_stage_id else None,
                "new_stage_id": str(request.stage_id),
            })

        return await self._to_dto(saved)

    async def _to_dto(self, document: Document) -> DocumentDTO:
        """Convert entity to DTO with related data."""
        doc_type = await self.doc_type_repo.get_by_id(document.document_type_id)
        stage = await self.stage_repo.get_by_id(document.stage_id) if document.stage_id else None
        folder = await self.folder_repo.get_by_id(document.folder_id) if document.folder_id else None

        return DocumentDTO(
            id=document.id,
            project_id=document.project_id,
            title=document.title,
            document_number=document.document_number,
            document_type_id=document.document_type_id,
            document_type_code=doc_type.code if doc_type else None,
            document_type_name=doc_type.name if doc_type else None,
            folder_id=document.folder_id,
            folder_path=folder.path if folder else None,
            stage_id=document.stage_id,
            stage_name=stage.name if stage else None,
            stage_color=stage.color if stage else None,
            version_scheme=document.version_scheme.value,
            current_version=document.current_version,
            status=document.status.value,
            description=document.description,
            tags=document.tags,
            metadata=document.metadata,
            external_references=document.external_references,
            created_by=document.created_by,
            updated_by=document.updated_by,
            is_archived=document.is_archived,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

    async def _log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: UUID,
        user_id: UUID,
        details: dict[str, Any],
    ) -> None:
        """Log an action to audit trail."""
        entry = AuditLogEntry(
            id=UUID(int=0),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            details=details,
        )
        await self.audit_repo.log(entry)


class VersioningService(ApplicationService):
    """Application service for document versioning."""

    def __init__(
        self,
        document_repo: IDocumentRepository,
        version_repo: IDocumentVersionRepository,
        doc_type_repo: IDocumentTypeRepository,
        storage: IDocumentStorage,
        audit_repo: IAuditLogRepository,
        naming_pattern: FileNamingPattern = FileNamingPattern.default(),
    ):
        self.document_repo = document_repo
        self.version_repo = version_repo
        self.doc_type_repo = doc_type_repo
        self.storage = storage
        self.audit_repo = audit_repo
        self.naming_pattern = naming_pattern

    async def upload_version(
        self,
        document_id: UUID,
        file_content: bytes,
        original_filename: str,
        mime_type: str,
        user_id: UUID,
        change_note: str = "",
        bump_type: str = "patch",
    ) -> DocumentVersionDTO:
        """Upload a new version of a document."""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Get latest version to determine next version
        latest = await self.version_repo.get_latest(document_id)

        if latest:
            # Increment version based on bump type
            match bump_type:
                case "major":
                    new_version = latest.version.increment_major()
                case "minor":
                    new_version = latest.version.increment_minor()
                case _:
                    new_version = latest.version.increment_patch()
        else:
            # First version
            new_version = Version.initial(document.version_scheme)

        # Generate filename
        doc_type = await self.doc_type_repo.get_by_id(document.document_type_id)
        context = {
            "document_name": document.title.replace(" ", "_"),
            "version": str(new_version),
            "date": date.today().isoformat(),
            "doc_type": doc_type.code if doc_type else "DOC",
            "ext": original_filename.split(".")[-1] if "." in original_filename else "bin",
        }
        generated_filename = self.naming_pattern.format(context)

        # Calculate checksum
        checksum = hashlib.sha256(file_content).hexdigest()

        # Create storage key
        storage_key = StorageKey.create(
            project_id=str(document.project_id),
            document_id=str(document.id),
            version=str(new_version),
            filename=generated_filename,
        )

        # Upload to storage
        await self.storage.upload(
            key=storage_key.key,
            content=file_content,
            content_type=mime_type,
            metadata={"document_id": str(document_id), "version": str(new_version)},
        )

        # Create version record
        version = DocumentVersion(
            id=UUID(int=0),
            document_id=document_id,
            version=new_version,
            storage_key=storage_key,
            original_filename=original_filename,
            generated_filename=generated_filename,
            mime_type=mime_type,
            size_bytes=len(file_content),
            checksum=checksum,
            change_note=change_note,
            uploaded_by=user_id,
        )

        saved_version = await self.version_repo.save(version)

        # Update document current version
        document.current_version = str(new_version)
        document.updated_by = user_id
        await self.document_repo.save(document)

        # Audit log
        entry = AuditLogEntry(
            id=UUID(int=0),
            action="version.uploaded",
            entity_type="document",
            entity_id=document_id,
            user_id=user_id,
            details={
                "version": str(new_version),
                "filename": original_filename,
                "size_bytes": len(file_content),
            },
        )
        await self.audit_repo.log(entry)

        return await self._to_dto(saved_version)

    async def list_versions(
        self,
        document_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> list[DocumentVersionDTO]:
        """List all versions of a document."""
        skip = (page - 1) * page_size
        versions = await self.version_repo.list_by_document(document_id, skip, page_size)
        return [await self._to_dto(v) for v in versions]

    async def get_version(self, version_id: UUID) -> Optional[DocumentVersionDTO]:
        """Get a specific version."""
        version = await self.version_repo.get_by_id(version_id)
        return await self._to_dto(version) if version else None

    async def get_download_url(
        self,
        version_id: UUID,
        expires_in: int = 3600,
    ) -> Optional[str]:
        """Get presigned download URL for a version."""
        version = await self.version_repo.get_by_id(version_id)
        if not version:
            return None

        presigned = await self.storage.get_presigned_download_url(
            key=version.storage_key.key,
            expires_in_seconds=expires_in,
            filename=version.generated_filename,
        )
        return presigned.url

    async def _to_dto(self, version: DocumentVersion) -> DocumentVersionDTO:
        """Convert version entity to DTO."""
        download_url = await self.storage.get_presigned_download_url(
            key=version.storage_key.key,
            filename=version.generated_filename,
        )

        return DocumentVersionDTO(
            id=version.id,
            document_id=version.document_id,
            version_string=str(version.version),
            original_filename=version.original_filename,
            generated_filename=version.generated_filename,
            mime_type=version.mime_type,
            size_bytes=version.size_bytes,
            checksum=version.checksum,
            change_note=version.change_note,
            uploaded_by=version.uploaded_by,
            uploaded_at=version.uploaded_at,
            download_url=download_url.url,
        )


class StageService(ApplicationService):
    """Application service for stage (Kanban) management."""

    def __init__(
        self,
        stage_repo: IStageRepository,
        document_repo: IDocumentRepository,
    ):
        self.stage_repo = stage_repo
        self.document_repo = document_repo

    async def create_stage(
        self,
        project_id: UUID,
        request: CreateStageRequest,
        user_id: UUID,
    ) -> StageDTO:
        """Create a new stage for a project."""
        # Get current stages to determine order
        existing = await self.stage_repo.list_by_project(project_id)
        order = len(existing)

        stage = Stage(
            id=UUID(int=0),
            project_id=project_id,
            name=request.name,
            description=request.description,
            order=order,
            color=request.color,
            is_default=request.is_default,
        )

        saved = await self.stage_repo.save(stage)
        return await self._to_dto(saved)

    async def list_stages(self, project_id: UUID) -> list[StageDTO]:
        """List all stages for a project."""
        stages = await self.stage_repo.list_by_project(project_id)
        return [await self._to_dto(s) for s in stages]

    async def update_stage(
        self,
        stage_id: UUID,
        request: UpdateStageRequest,
    ) -> Optional[StageDTO]:
        """Update a stage."""
        stage = await self.stage_repo.get_by_id(stage_id)
        if not stage:
            return None

        if request.name is not None:
            stage.name = request.name
        if request.description is not None:
            stage.description = request.description
        if request.color is not None:
            stage.color = request.color

        saved = await self.stage_repo.save(stage)
        return await self._to_dto(saved)

    async def reorder_stages(
        self,
        project_id: UUID,
        stage_ids: list[UUID],
    ) -> list[StageDTO]:
        """Reorder stages."""
        await self.stage_repo.reorder(project_id, stage_ids)
        return await self.list_stages(project_id)

    async def get_kanban_board(self, project_id: UUID) -> KanbanBoardResponse:
        """Get full Kanban board data."""
        stages = await self.stage_repo.list_by_project(project_id)
        stage_dtos = [await self._to_dto(s) for s in stages]

        documents_by_stage: dict[str, list[DocumentDTO]] = {}
        for stage in stages:
            docs = await self.document_repo.list_by_project(
                project_id=project_id,
                stage_id=stage.id,
            )
            # Simplified conversion - in production, reuse DocumentService._to_dto
            documents_by_stage[str(stage.id)] = [
                DocumentDTO(
                    id=d.id,
                    project_id=d.project_id,
                    title=d.title,
                    document_number=d.document_number,
                    document_type_id=d.document_type_id,
                    folder_id=d.folder_id,
                    stage_id=d.stage_id,
                    version_scheme=d.version_scheme.value,
                    current_version=d.current_version,
                    status=d.status.value,
                    description=d.description,
                    tags=d.tags,
                    metadata=d.metadata,
                    external_references=d.external_references,
                    created_by=d.created_by,
                    updated_by=d.updated_by,
                    is_archived=d.is_archived,
                    created_at=d.created_at,
                    updated_at=d.updated_at,
                )
                for d in docs
            ]

        return KanbanBoardResponse(
            project_id=project_id,
            stages=stage_dtos,
            documents_by_stage=documents_by_stage,
        )

    async def _to_dto(self, stage: Stage) -> StageDTO:
        """Convert stage entity to DTO."""
        doc_count = await self.document_repo.count_by_project(
            project_id=stage.project_id,
            stage_id=stage.id,
        )

        return StageDTO(
            id=stage.id,
            project_id=stage.project_id,
            name=stage.name,
            description=stage.description,
            order=stage.order,
            color=stage.color,
            is_default=stage.is_default,
            document_count=doc_count,
            created_at=stage.created_at,
            updated_at=stage.updated_at,
        )


class FolderService(ApplicationService):
    """Application service for folder management."""

    def __init__(self, folder_repo: IFolderRepository):
        self.folder_repo = folder_repo

    async def create_folder(
        self,
        request: CreateFolderRequest,
        user_id: UUID,
    ) -> FolderDTO:
        """Create a new folder."""
        path = f"/{request.name}"
        if request.parent_id:
            parent = await self.folder_repo.get_by_id(request.parent_id)
            if parent:
                path = f"{parent.path}/{request.name}"

        folder = Folder(
            id=UUID(int=0),
            project_id=request.project_id,
            name=request.name,
            path=path,
            parent_id=request.parent_id,
            description=request.description,
            created_by=user_id,
        )

        saved = await self.folder_repo.save(folder)
        return self._to_dto(saved)

    async def list_folders(
        self,
        project_id: UUID,
        parent_id: Optional[UUID] = None,
    ) -> list[FolderDTO]:
        """List folders."""
        folders = await self.folder_repo.list_by_project(project_id, parent_id)
        return [self._to_dto(f) for f in folders]

    def _to_dto(self, folder: Folder) -> FolderDTO:
        """Convert folder entity to DTO."""
        return FolderDTO(
            id=folder.id,
            project_id=folder.project_id,
            name=folder.name,
            path=folder.path,
            parent_id=folder.parent_id,
            description=folder.description,
            document_count=0,  # TODO: count documents
            is_archived=folder.is_archived,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
        )


class DocumentTypeService(ApplicationService):
    """Application service for document type management."""

    def __init__(self, doc_type_repo: IDocumentTypeRepository):
        self.doc_type_repo = doc_type_repo

    async def create_type(
        self,
        request: CreateDocumentTypeRequest,
    ) -> DocumentTypeDTO:
        """Create a new document type."""
        doc_type = DocumentType(
            id=UUID(int=0),
            code=request.code.upper(),
            name=request.name,
            description=request.description,
            category=request.category,
        )

        saved = await self.doc_type_repo.save(doc_type)
        return self._to_dto(saved)

    async def list_types(
        self,
        category: Optional[str] = None,
        include_inactive: bool = False,
    ) -> list[DocumentTypeDTO]:
        """List document types."""
        types = await self.doc_type_repo.list_all(category, include_inactive)
        return [self._to_dto(t) for t in types]

    async def update_type(
        self,
        type_id: UUID,
        request: UpdateDocumentTypeRequest,
    ) -> Optional[DocumentTypeDTO]:
        """Update a document type."""
        doc_type = await self.doc_type_repo.get_by_id(type_id)
        if not doc_type:
            return None

        if request.name is not None:
            doc_type.name = request.name
        if request.description is not None:
            doc_type.description = request.description
        if request.category is not None:
            doc_type.category = request.category
        if request.is_active is not None:
            doc_type.is_active = request.is_active

        saved = await self.doc_type_repo.save(doc_type)
        return self._to_dto(saved)

    def _to_dto(self, doc_type: DocumentType) -> DocumentTypeDTO:
        """Convert entity to DTO."""
        return DocumentTypeDTO(
            id=doc_type.id,
            code=doc_type.code,
            name=doc_type.name,
            description=doc_type.description,
            category=doc_type.category,
            is_active=doc_type.is_active,
            created_at=doc_type.created_at,
            updated_at=doc_type.updated_at,
        )


class StorageTemplateService(ApplicationService):
    """Application service for storage template management."""

    def __init__(
        self,
        template_repo: IStorageTemplateRepository,
        template_folder_repo: ITemplateFolderRepository,
        folder_repo: IFolderRepository,
    ):
        self.template_repo = template_repo
        self.template_folder_repo = template_folder_repo
        self.folder_repo = folder_repo

    async def create_template(
        self,
        request: CreateStorageTemplateRequest,
        user_id: UUID,
    ) -> StorageTemplateDTO:
        """Create a new storage template."""
        template = StorageTemplate(
            id=UUID(int=0),
            name=request.name,
            description=request.description,
            is_default=request.is_default,
            created_by=user_id,
        )

        saved = await self.template_repo.save(template)

        # Create template folders
        for idx, folder_data in enumerate(request.folders):
            folder = TemplateFolder(
                id=UUID(int=0),
                template_id=saved.id,
                name=folder_data.get("name", ""),
                path=folder_data.get("path", ""),
                description=folder_data.get("description", ""),
                order=idx,
            )
            await self.template_folder_repo.save(folder)

        return await self._to_dto(saved)

    async def list_templates(
        self,
        include_inactive: bool = False,
    ) -> list[StorageTemplateDTO]:
        """List all templates."""
        templates = await self.template_repo.list_all(include_inactive)
        return [await self._to_dto(t) for t in templates]

    async def apply_template(
        self,
        project_id: UUID,
        template_id: UUID,
        user_id: UUID,
    ) -> list[FolderDTO]:
        """Apply a template to a project (create folders)."""
        template_folders = await self.template_folder_repo.list_by_template(template_id)
        created_folders: list[FolderDTO] = []

        for tf in template_folders:
            folder = Folder(
                id=UUID(int=0),
                project_id=project_id,
                name=tf.name,
                path=tf.path,
                description=tf.description,
                created_by=user_id,
            )
            saved = await self.folder_repo.save(folder)
            created_folders.append(FolderDTO(
                id=saved.id,
                project_id=saved.project_id,
                name=saved.name,
                path=saved.path,
                parent_id=saved.parent_id,
                description=saved.description,
                document_count=0,
                is_archived=saved.is_archived,
                created_at=saved.created_at,
                updated_at=saved.updated_at,
            ))

        return created_folders

    async def _to_dto(self, template: StorageTemplate) -> StorageTemplateDTO:
        """Convert entity to DTO."""
        folders = await self.template_folder_repo.list_by_template(template.id)

        return StorageTemplateDTO(
            id=template.id,
            name=template.name,
            description=template.description,
            is_default=template.is_default,
            is_active=template.is_active,
            folder_count=len(folders),
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
