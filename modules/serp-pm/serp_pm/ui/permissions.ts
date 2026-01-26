/**
 * PM Module Permissions
 * Must match backend permissions in serp_pm/interfaces/permissions.py
 */

export const PM_PERMISSIONS = {
    // Projects
    PROJECT_LIST: 'pm.project.list',
    PROJECT_READ: 'pm.project.read',
    PROJECT_CREATE: 'pm.project.create',
    PROJECT_UPDATE: 'pm.project.update',
    PROJECT_DELETE: 'pm.project.delete',

    // Tasks
    TASK_LIST: 'pm.task.list',
    TASK_READ: 'pm.task.read',
    TASK_CREATE: 'pm.task.create',
    TASK_UPDATE: 'pm.task.update',
    TASK_DELETE: 'pm.task.delete',
    TASK_ASSIGN: 'pm.task.assign',

    // Teams
    TEAM_LIST: 'pm.team.list',
    TEAM_READ: 'pm.team.read',
    TEAM_CREATE: 'pm.team.create',
    TEAM_MANAGE_MEMBERS: 'pm.team.manage_members',
} as const;

export function getAllPMPermissions(): string[] {
    return Object.values(PM_PERMISSIONS);
}
