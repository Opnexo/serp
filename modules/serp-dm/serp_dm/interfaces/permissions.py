"""
Permission definitions for Document Management module.
"""

from serp_core.auth.permissions import Permission


# Document permissions
DOCUMENT_LIST = Permission(
    name="dm.document.list",
    description="List documents",
)

DOCUMENT_READ = Permission(
    name="dm.document.read",
    description="Read document details",
)

DOCUMENT_CREATE = Permission(
    name="dm.document.create",
    description="Create documents",
)

DOCUMENT_UPDATE = Permission(
    name="dm.document.update",
    description="Update documents",
)

DOCUMENT_DELETE = Permission(
    name="dm.document.delete",
    description="Delete documents",
)

DOCUMENT_DOWNLOAD = Permission(
    name="dm.document.download",
    description="Download document files",
)

# Folder permissions
FOLDER_LIST = Permission(
    name="dm.folder.list",
    description="List folders",
)

FOLDER_READ = Permission(
    name="dm.folder.read",
    description="Read folder details",
)

FOLDER_CREATE = Permission(
    name="dm.folder.create",
    description="Create folders",
)

FOLDER_UPDATE = Permission(
    name="dm.folder.update",
    description="Update folders",
)

FOLDER_DELETE = Permission(
    name="dm.folder.delete",
    description="Delete folders",
)

# All permissions
ALL_PERMISSIONS = [
    DOCUMENT_LIST,
    DOCUMENT_READ,
    DOCUMENT_CREATE,
    DOCUMENT_UPDATE,
    DOCUMENT_DELETE,
    DOCUMENT_DOWNLOAD,
    FOLDER_LIST,
    FOLDER_READ,
    FOLDER_CREATE,
    FOLDER_UPDATE,
    FOLDER_DELETE,
]
