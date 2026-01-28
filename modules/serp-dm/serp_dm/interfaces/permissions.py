"""
Permission definitions for Document Management module.

Permissions follow the pattern: dm.<resource>.<action>
Team-based permissions from PM module are respected for project access.
"""

from serp_core.auth.permissions import Permission


class DMPermissions:
    """Document Management module permissions."""

    # =========================================================================
    # Document Permissions
    # =========================================================================
    DOCUMENT_LIST = "dm.document.list"
    DOCUMENT_READ = "dm.document.read"
    DOCUMENT_CREATE = "dm.document.create"
    DOCUMENT_UPDATE = "dm.document.update"
    DOCUMENT_DELETE = "dm.document.delete"
    DOCUMENT_UPLOAD_VERSION = "dm.document.upload_version"
    DOCUMENT_DOWNLOAD = "dm.document.download"
    DOCUMENT_MOVE_STAGE = "dm.document.move_stage"
    DOCUMENT_SUBMIT_APPROVAL = "dm.document.submit_approval"

    # =========================================================================
    # Stage (Kanban) Permissions
    # =========================================================================
    STAGE_LIST = "dm.stage.list"
    STAGE_MANAGE = "dm.stage.manage"  # Create, update, delete, reorder

    # =========================================================================
    # Folder Permissions
    # =========================================================================
    FOLDER_LIST = "dm.folder.list"
    FOLDER_READ = "dm.folder.read"
    FOLDER_CREATE = "dm.folder.create"
    FOLDER_UPDATE = "dm.folder.update"
    FOLDER_DELETE = "dm.folder.delete"

    # =========================================================================
    # Template Permissions (Admin)
    # =========================================================================
    TEMPLATE_LIST = "dm.template.list"
    TEMPLATE_MANAGE = "dm.template.manage"  # Create, update, delete

    # =========================================================================
    # Document Type Permissions (Admin)
    # =========================================================================
    DOCTYPE_LIST = "dm.doctype.list"
    DOCTYPE_MANAGE = "dm.doctype.manage"  # Create, update, delete

    # =========================================================================
    # Approval Permissions
    # =========================================================================
    APPROVAL_VIEW = "dm.approval.view"
    APPROVAL_DECIDE = "dm.approval.decide"  # Approve/reject/return

    # =========================================================================
    # Export Permissions
    # =========================================================================
    PROJECT_EXPORT = "dm.project.export"  # Export project docs as ZIP

    # =========================================================================
    # Audit Permissions (Admin)
    # =========================================================================
    AUDIT_VIEW = "dm.audit.view"


# Permission objects for registration
DOCUMENT_LIST = Permission(
    code=DMPermissions.DOCUMENT_LIST,
    name="Document List",
    description="List documents in a project",
)

DOCUMENT_READ = Permission(
    code=DMPermissions.DOCUMENT_READ,
    name="Document Read",
    description="Read document details",
)

DOCUMENT_CREATE = Permission(
    code=DMPermissions.DOCUMENT_CREATE,
    name="Document Create",
    description="Register new documents",
)

DOCUMENT_UPDATE = Permission(
    code=DMPermissions.DOCUMENT_UPDATE,
    name="Document Update",
    description="Update document metadata",
)

DOCUMENT_DELETE = Permission(
    code=DMPermissions.DOCUMENT_DELETE,
    name="Document Delete",
    description="Archive/delete documents",
)

DOCUMENT_UPLOAD_VERSION = Permission(
    code=DMPermissions.DOCUMENT_UPLOAD_VERSION,
    name="Document Upload Version",
    description="Upload new document versions",
)

DOCUMENT_DOWNLOAD = Permission(
    code=DMPermissions.DOCUMENT_DOWNLOAD,
    name="Document Download",
    description="Download document files",
)

DOCUMENT_MOVE_STAGE = Permission(
    code=DMPermissions.DOCUMENT_MOVE_STAGE,
    name="Document Move Stage",
    description="Move documents between stages",
)

STAGE_LIST = Permission(
    code=DMPermissions.STAGE_LIST,
    name="Stage List",
    description="List project stages",
)

STAGE_MANAGE = Permission(
    code=DMPermissions.STAGE_MANAGE,
    name="Stage Manage",
    description="Manage project stages (create, update, delete, reorder)",
)

FOLDER_LIST = Permission(
    code=DMPermissions.FOLDER_LIST,
    name="Folder List",
    description="List folders",
)

FOLDER_READ = Permission(
    code=DMPermissions.FOLDER_READ,
    name="Folder Read",
    description="Read folder details",
)

FOLDER_CREATE = Permission(
    code=DMPermissions.FOLDER_CREATE,
    name="Folder Create",
    description="Create folders",
)

FOLDER_UPDATE = Permission(
    code=DMPermissions.FOLDER_UPDATE,
    name="Folder Update",
    description="Update folders",
)

FOLDER_DELETE = Permission(
    code=DMPermissions.FOLDER_DELETE,
    name="Folder Delete",
    description="Delete folders",
)

TEMPLATE_LIST = Permission(
    code=DMPermissions.TEMPLATE_LIST,
    name="Template List",
    description="List storage templates",
)

TEMPLATE_MANAGE = Permission(
    code=DMPermissions.TEMPLATE_MANAGE,
    name="Template Manage",
    description="Manage storage templates (admin)",
)

DOCTYPE_LIST = Permission(
    code=DMPermissions.DOCTYPE_LIST,
    name="Doc Type List",
    description="List document types",
)

DOCTYPE_MANAGE = Permission(
    code=DMPermissions.DOCTYPE_MANAGE,
    name="Doc Type Manage",
    description="Manage document types (admin)",
)

APPROVAL_VIEW = Permission(
    code=DMPermissions.APPROVAL_VIEW,
    name="Approval View",
    description="View approval requests",
)

APPROVAL_DECIDE = Permission(
    code=DMPermissions.APPROVAL_DECIDE,
    name="Approval Decide",
    description="Make approval decisions",
)

PROJECT_EXPORT = Permission(
    code=DMPermissions.PROJECT_EXPORT,
    name="Project Export",
    description="Export project documents as ZIP",
)

AUDIT_VIEW = Permission(
    code=DMPermissions.AUDIT_VIEW,
    name="Audit View",
    description="View audit logs (admin)",
)


# All permissions for module registration
ALL_PERMISSIONS = [
    DOCUMENT_LIST,
    DOCUMENT_READ,
    DOCUMENT_CREATE,
    DOCUMENT_UPDATE,
    DOCUMENT_DELETE,
    DOCUMENT_UPLOAD_VERSION,
    DOCUMENT_DOWNLOAD,
    DOCUMENT_MOVE_STAGE,
    STAGE_LIST,
    STAGE_MANAGE,
    FOLDER_LIST,
    FOLDER_READ,
    FOLDER_CREATE,
    FOLDER_UPDATE,
    FOLDER_DELETE,
    TEMPLATE_LIST,
    TEMPLATE_MANAGE,
    DOCTYPE_LIST,
    DOCTYPE_MANAGE,
    APPROVAL_VIEW,
    APPROVAL_DECIDE,
    PROJECT_EXPORT,
    AUDIT_VIEW,
]


def get_all_dm_permissions() -> list[str]:
    """Get all DM permission codes as strings."""
    return [p.code for p in ALL_PERMISSIONS]

