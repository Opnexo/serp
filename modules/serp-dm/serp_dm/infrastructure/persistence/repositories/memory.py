"""
In-memory repository implementations for testing.
"""

from typing import Optional
from uuid import UUID, uuid4

from serp_dm.domain.entities import (
    ApprovalRequest,
    AuditLogEntry,
    Document,
    DocumentType,
    DocumentVersion,
    Folder,
    Project,
    Stage,
    StageTemplate,
    StageTemplateItem,
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
    IProjectRepository,
    IStageRepository,
    IStageTemplateRepository,
    IStorageTemplateRepository,
    ITemplateFolderRepository,
)
from serp_dm.domain.value_objects import ApprovalStatus


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


class InMemoryStageRepository(IStageRepository):
    """In-memory stage repository for testing."""

    def __init__(self):
        self._stages: dict[UUID, Stage] = {}

    async def get_by_id(self, id: UUID) -> Optional[Stage]:
        return self._stages.get(id)

    async def get_default(self, project_id: UUID) -> Optional[Stage]:
        for stage in self._stages.values():
            if stage.project_id == project_id and stage.is_default:
                return stage
        return None

    async def list_by_project(self, project_id: UUID) -> list[Stage]:
        stages = [s for s in self._stages.values() if s.project_id == project_id]
        return sorted(stages, key=lambda s: s.position)

    async def save(self, stage: Stage) -> Stage:
        if stage.id == UUID(int=0):
            stage.id = uuid4()
        self._stages[stage.id] = stage
        return stage

    async def delete(self, id: UUID) -> None:
        self._stages.pop(id, None)


class InMemoryStorageTemplateRepository(IStorageTemplateRepository):
    """In-memory storage template repository for testing."""

    def __init__(self):
        self._templates: dict[UUID, StorageTemplate] = {}

    async def get_by_id(self, id: UUID) -> Optional[StorageTemplate]:
        return self._templates.get(id)

    async def get_default(self) -> Optional[StorageTemplate]:
        for template in self._templates.values():
            if template.is_default:
                return template
        return None

    async def list_all(self, include_inactive: bool = False) -> list[StorageTemplate]:
        if include_inactive:
            return list(self._templates.values())
        return [t for t in self._templates.values() if t.is_active]

    async def save(self, template: StorageTemplate) -> StorageTemplate:
        if template.id == UUID(int=0):
            template.id = uuid4()
        self._templates[template.id] = template
        return template

    async def delete(self, id: UUID) -> None:
        self._templates.pop(id, None)


class InMemoryStageTemplateRepository(IStageTemplateRepository):
    """In-memory stage template repository for testing."""

    def __init__(self):
        self._templates: dict[UUID, StageTemplate] = {}
        self._items: dict[UUID, StageTemplateItem] = {}

    async def get_by_id(self, id: UUID) -> Optional[StageTemplate]:
        return self._templates.get(id)

    async def list_all(self) -> list[StageTemplate]:
        return list(self._templates.values())

    async def save(self, template: StageTemplate) -> StageTemplate:
        if template.id == UUID(int=0):
            template.id = uuid4()
        self._templates[template.id] = template
        return template

    async def list_items(self, template_id: UUID) -> list[StageTemplateItem]:
        items = [item for item in self._items.values() if item.template_id == template_id]
        return sorted(items, key=lambda i: i.order)

    async def save_item(self, item: StageTemplateItem) -> StageTemplateItem:
        if item.id == UUID(int=0):
            item.id = uuid4()
        self._items[item.id] = item
        return item


class InMemoryProjectRepository(IProjectRepository):
    """In-memory project repository for testing."""

    def __init__(self):
        self._projects: dict[UUID, Project] = {}

    async def get_by_pm_id(self, pm_project_id: UUID) -> Optional[Project]:
        for project in self._projects.values():
            if project.pm_project_id == pm_project_id:
                return project
        return None

    async def list_all(self) -> list[Project]:
        return list(self._projects.values())

    async def save(self, project: Project) -> Project:
        if project.id == UUID(int=0):
            project.id = uuid4()
        self._projects[project.id] = project
        return project


class InMemoryTemplateFolderRepository(ITemplateFolderRepository):
    """In-memory template folder repository for testing."""

    def __init__(self):
        self._folders: dict[UUID, TemplateFolder] = {}

    async def get_by_id(self, id: UUID) -> Optional[TemplateFolder]:
        return self._folders.get(id)

    async def list_by_template(self, template_id: UUID) -> list[TemplateFolder]:
        return [f for f in self._folders.values() if f.template_id == template_id]

    async def save(self, folder: TemplateFolder) -> TemplateFolder:
        if folder.id == UUID(int=0):
            folder.id = uuid4()
        self._folders[folder.id] = folder
        return folder

    async def delete(self, id: UUID) -> None:
        self._folders.pop(id, None)

    async def count_by_template(self, template_id: UUID) -> int:
        return len([f for f in self._folders.values() if f.template_id == template_id])


class InMemoryDocumentTypeRepository(IDocumentTypeRepository):
    """In-memory document type repository for testing."""

    def __init__(self):
        self._types: dict[UUID, DocumentType] = {}

    async def get_by_id(self, id: UUID) -> Optional[DocumentType]:
        return self._types.get(id)

    async def get_by_code(self, code: str) -> Optional[DocumentType]:
        for doc_type in self._types.values():
            if doc_type.code == code:
                return doc_type
        return None

    async def list_all(
        self,
        category: Optional[str] = None,
        include_inactive: bool = False,
    ) -> list[DocumentType]:
        types = list(self._types.values())
        if category:
            types = [t for t in types if t.category == category]
        if not include_inactive:
            types = [t for t in types if t.is_active]
        return types

    async def save(self, doc_type: DocumentType) -> DocumentType:
        if doc_type.id == UUID(int=0):
            doc_type.id = uuid4()
        self._types[doc_type.id] = doc_type
        return doc_type


class InMemoryApprovalRequestRepository(IApprovalRequestRepository):
    """In-memory approval request repository for testing."""

    def __init__(self):
        self._requests: dict[UUID, ApprovalRequest] = {}

    async def get_by_id(self, id: UUID) -> Optional[ApprovalRequest]:
        return self._requests.get(id)

    async def list_by_document(self, document_id: UUID) -> list[ApprovalRequest]:
        return [r for r in self._requests.values() if r.document_id == document_id]

    async def list_pending_for_user(self, user_id: UUID) -> list[ApprovalRequest]:
        return [
            r
            for r in self._requests.values()
            if r.approver_id == user_id and r.status == ApprovalStatus.PENDING
        ]

    async def list_by_status(
        self,
        status: ApprovalStatus,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ApprovalRequest]:
        requests = [r for r in self._requests.values() if r.status == status]
        return requests[skip : skip + limit]

    async def save(self, request: ApprovalRequest) -> ApprovalRequest:
        if request.id == UUID(int=0):
            request.id = uuid4()
        self._requests[request.id] = request
        return request


class InMemoryAuditLogRepository(IAuditLogRepository):
    """In-memory audit log repository for testing."""

    def __init__(self):
        self._logs: dict[UUID, AuditLogEntry] = {}

    async def log(self, entry: AuditLogEntry) -> AuditLogEntry:
        if entry.id == UUID(int=0):
            entry.id = uuid4()
        self._logs[entry.id] = entry
        return entry

    async def list_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        entries = [
            e
            for e in self._logs.values()
            if e.entity_type == entity_type and e.entity_id == entity_id
        ]
        return sorted(entries, key=lambda e: e.timestamp, reverse=True)[
            skip : skip + limit
        ]

    async def list_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        entries = [e for e in self._logs.values() if e.user_id == user_id]
        return sorted(entries, key=lambda e: e.timestamp, reverse=True)[
            skip : skip + limit
        ]
