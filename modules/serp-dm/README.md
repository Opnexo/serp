# SERP Document Management Module

Document and file management system for the SERP platform.

## Features

- **Document Management**: Create, update, delete, and organize documents
- **Folder Organization**: Hierarchical folder structure for document organization
- **File Metadata**: Track file size, type, version, and checksums
- **Access Control**: Permission-based access to documents and folders
- **Version History**: Track document versions and changes
- **Search & Filter**: Find documents by name, type, tags, or metadata

## Installation

```bash
uv add serp-dm
```

## Quick Start

### 1. Register the module

The module auto-registers via entry points. Just install and it's available.

### 2. Configure

```python
# config.py
from serp_dm.config import DMSettings

settings = DMSettings(
    database_schema="dm",
    max_file_size_mb=100,
    allowed_file_types=["pdf", "docx", "txt", "jpg", "png"],
)
```

### 3. Use in your app

```python
from serp_dm.application.services import DocumentService, FolderService
from serp_dm.infrastructure.persistence.repositories import PostgresDocumentRepository

# Create services
doc_repo = PostgresDocumentRepository(db_session)
doc_service = DocumentService(doc_repo)

# Create a document
document = await doc_service.create_document(
    name="Project Proposal.pdf",
    folder_id=folder_id,
    file_path="/uploads/proposal.pdf",
    mime_type="application/pdf",
    size_bytes=1024000
)

# List documents in a folder
documents = await doc_service.list_documents(folder_id=folder_id)
```

## API Endpoints

All endpoints are registered at `/api/dm/*`:

### Documents
- `GET /api/dm/documents` - List documents (paginated)
- `GET /api/dm/documents/{id}` - Get document by ID
- `POST /api/dm/documents` - Create document
- `PUT /api/dm/documents/{id}` - Update document
- `DELETE /api/dm/documents/{id}` - Delete document
- `GET /api/dm/documents/{id}/download` - Download document file

### Folders
- `GET /api/dm/folders` - List folders
- `GET /api/dm/folders/{id}` - Get folder by ID
- `POST /api/dm/folders` - Create folder
- `PUT /api/dm/folders/{id}` - Update folder
- `DELETE /api/dm/folders/{id}` - Delete folder

## Permissions

Module permissions follow the pattern `dm:<resource>:<action>`:

### Document Permissions
- `dm.document.list` - List documents
- `dm.document.read` - Read document details
- `dm.document.create` - Create documents
- `dm.document.update` - Update documents
- `dm.document.delete` - Delete documents
- `dm.document.download` - Download document files

### Folder Permissions
- `dm.folder.list` - List folders
- `dm.folder.read` - Read folder details
- `dm.folder.create` - Create folders
- `dm.folder.update` - Update folders
- `dm.folder.delete` - Delete folders

## Domain Model

### Document (Aggregate Root)

```python
@dataclass
class Document(AggregateRoot):
    name: str
    folder_id: Optional[UUID]
    file_path: str
    mime_type: str
    size_bytes: int
    checksum: str
    version: int
    created_by: UUID
    updated_by: UUID
    tags: List[str]
    metadata: Dict[str, Any]
```

### Folder (Entity)

```python
@dataclass
class Folder(Entity):
    name: str
    parent_id: Optional[UUID]
    description: str
    created_by: UUID
    path: str
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy serp_dm

# Linting
uv run ruff check serp_dm
```

## License

MIT License - See LICENSE file for details
