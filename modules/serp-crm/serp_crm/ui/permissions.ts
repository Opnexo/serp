/**
 * CRM Module Permissions
 * Must match backend permissions in serp_crm/__init__.py MODULE_INFO
 */

export const CRM_PERMISSIONS = {
    // Partners
    PARTNER_LIST: 'crm:partners:list',
    PARTNER_READ: 'crm:partners:read',
    PARTNER_CREATE: 'crm:partners:create',
    PARTNER_UPDATE: 'crm:partners:update',
    PARTNER_DELETE: 'crm:partners:delete',

    // Contacts
    CONTACT_LIST: 'crm:contacts:list',
    CONTACT_READ: 'crm:contacts:read',
    CONTACT_CREATE: 'crm:contacts:create',
    CONTACT_UPDATE: 'crm:contacts:update',
    CONTACT_DELETE: 'crm:contacts:delete',

    // Leads
    LEAD_LIST: 'crm:leads:list',
    LEAD_READ: 'crm:leads:read',
    LEAD_CREATE: 'crm:leads:create',
    LEAD_UPDATE: 'crm:leads:update',
    LEAD_DELETE: 'crm:leads:delete',

    // Opportunities
    OPPORTUNITY_LIST: 'crm:opportunities:list',
    OPPORTUNITY_READ: 'crm:opportunities:read',
    OPPORTUNITY_CREATE: 'crm:opportunities:create',
    OPPORTUNITY_UPDATE: 'crm:opportunities:update',
    OPPORTUNITY_DELETE: 'crm:opportunities:delete',
} as const;

export function getAllCRMPermissions(): string[] {
    return Object.values(CRM_PERMISSIONS);
}
