/**
 * DM Module Permissions
 * Must match backend permissions in serp_dm/interfaces/permissions.py
 */

export const DM_PERMISSIONS = {
    // Documents
    DOCUMENT_LIST: 'dm.document.list',
    DOCUMENT_READ: 'dm.document.read',
    DOCUMENT_CREATE: 'dm.document.create',
    DOCUMENT_UPDATE: 'dm.document.update',
    DOCUMENT_DELETE: 'dm.document.delete',
    DOCUMENT_UPLOAD_VERSION: 'dm.document.upload_version',
    DOCUMENT_DOWNLOAD: 'dm.document.download',
    DOCUMENT_MOVE_STAGE: 'dm.document.move_stage',
    DOCUMENT_SUBMIT_APPROVAL: 'dm.document.submit_approval',

    // Stages (Kanban)
    STAGE_LIST: 'dm.stage.list',
    STAGE_MANAGE: 'dm.stage.manage',

    // Folders
    FOLDER_LIST: 'dm.folder.list',
    FOLDER_READ: 'dm.folder.read',
    FOLDER_CREATE: 'dm.folder.create',
    FOLDER_UPDATE: 'dm.folder.update',
    FOLDER_DELETE: 'dm.folder.delete',

    // Templates (Admin)
    TEMPLATE_LIST: 'dm.template.list',
    TEMPLATE_MANAGE: 'dm.template.manage',

    // Document Types (Admin)
    DOCTYPE_LIST: 'dm.doctype.list',
    DOCTYPE_MANAGE: 'dm.doctype.manage',

    // Approvals
    APPROVAL_VIEW: 'dm.approval.view',
    APPROVAL_DECIDE: 'dm.approval.decide',

    // Export
    PROJECT_EXPORT: 'dm.project.export',

    // Audit (Admin)
    AUDIT_VIEW: 'dm.audit.view',
} as const;

export type DMPermission = (typeof DM_PERMISSIONS)[keyof typeof DM_PERMISSIONS];

export function getAllDMPermissions(): string[] {
    return Object.values(DM_PERMISSIONS);
}
