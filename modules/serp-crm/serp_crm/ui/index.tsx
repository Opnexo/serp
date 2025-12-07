/**
 * CRM Module UI Entry Point
 *
 * This file exports all UI components for the CRM module.
 * When the bundle is loaded by the shell, these components
 * are registered in the global component registry.
 */

// Views
export { default as PartnersListView } from './views/PartnersListView';
export { default as PartnerDetailView } from './views/PartnerDetailView';
export { default as PartnerEditView } from './views/PartnerEditView';

// Re-export API clients for use by views
export * from './api/partners';

// Module metadata
export const MODULE_ID = 'crm';
export const MODULE_NAME = 'CRM';
export const MODULE_VERSION = '0.1.0';

/**
 * Component map for dynamic loading
 * Maps component names (from backend config) to actual components
 */
export const components = {
    PartnersListView: () => import('./views/PartnersListView'),
    PartnerDetailView: () => import('./views/PartnerDetailView'),
    PartnerEditView: () => import('./views/PartnerEditView'),
    // Add more views as they are created
    ContactsListView: () => Promise.resolve({ default: () => <div>Contacts List - Coming Soon</div> }),
    LeadsListView: () => Promise.resolve({ default: () => <div>Leads List - Coming Soon</div> }),
    OpportunitiesListView: () => Promise.resolve({ default: () => <div>Opportunities List - Coming Soon</div> }),
};

/**
 * Get a component by name
 */
export function getComponent(name: string) {
    return components[name as keyof typeof components];
}
