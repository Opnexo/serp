/**
 * Permission constants for common module.
 * MUST MATCH backend permissions in common_permissions.py
 */

export const COMMON_PERMISSIONS = {
    // Addresses
    ADDRESS_LIST: 'common:addresses:list',
    ADDRESS_READ: 'common:addresses:read',
    ADDRESS_CREATE: 'common:addresses:create',
    ADDRESS_UPDATE: 'common:addresses:update',
    ADDRESS_DELETE: 'common:addresses:delete',
} as const;

export type CommonPermission = (typeof COMMON_PERMISSIONS)[keyof typeof COMMON_PERMISSIONS];

export function getAllCommonPermissions(): string[] {
    return Object.values(COMMON_PERMISSIONS);
}
