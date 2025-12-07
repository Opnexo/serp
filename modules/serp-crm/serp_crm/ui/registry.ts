import type { ModuleRegistry } from '@/types';
import { CRM_PERMISSIONS, getAllCRMPermissions } from './permissions';

/**
 * CRM Module Registry
 * Defines the module's ribbon tab, buttons, and routes
 */
export const crmModuleRegistry: ModuleRegistry = {
    moduleId: 'crm',
    moduleName: 'CRM',
    version: '0.1.0',
    icon: 'Users',
    description: 'Customer Relationship Management',

    ribbon: {
        tabId: 'crm',
        tabLabel: 'CRM',
        tabIcon: 'Users',
        tabOrder: 10,
        groups: [
            {
                groupId: 'crm-partners',
                groupLabel: 'Partners',
                groupOrder: 1,
                buttons: [
                    {
                        buttonId: 'crm-partners-list',
                        label: 'Partners',
                        icon: 'Building2',
                        permission: CRM_PERMISSIONS.PARTNER_LIST,
                        action: {
                            type: 'navigate',
                            route: '/crm/partners',
                        },
                        buttonOrder: 1,
                        tooltip: 'View all partners',
                    },
                    {
                        buttonId: 'crm-partners-new',
                        label: 'New Partner',
                        icon: 'Plus',
                        permission: CRM_PERMISSIONS.PARTNER_CREATE,
                        action: {
                            type: 'navigate',
                            route: '/crm/partners/new',
                        },
                        variant: 'primary',
                        buttonOrder: 2,
                        tooltip: 'Create a new partner',
                    },
                    {
                        buttonId: 'crm-contacts-list',
                        label: 'Contacts',
                        icon: 'Contact',
                        permission: CRM_PERMISSIONS.CONTACT_LIST,
                        action: {
                            type: 'navigate',
                            route: '/crm/contacts',
                        },
                        buttonOrder: 3,
                        tooltip: 'View all contacts',
                    },
                ],
            },
            {
                groupId: 'crm-sales',
                groupLabel: 'Sales',
                groupOrder: 2,
                buttons: [
                    {
                        buttonId: 'crm-leads-list',
                        label: 'Leads',
                        icon: 'UserPlus',
                        permission: CRM_PERMISSIONS.LEAD_LIST,
                        action: {
                            type: 'navigate',
                            route: '/crm/leads',
                        },
                        buttonOrder: 1,
                        tooltip: 'View all leads',
                    },
                    {
                        buttonId: 'crm-leads-new',
                        label: 'New Lead',
                        icon: 'Plus',
                        permission: CRM_PERMISSIONS.LEAD_CREATE,
                        action: {
                            type: 'navigate',
                            route: '/crm/leads/new',
                        },
                        buttonOrder: 2,
                        tooltip: 'Create a new lead',
                    },
                    {
                        buttonId: 'crm-opportunities-list',
                        label: 'Opportunities',
                        icon: 'Target',
                        permission: CRM_PERMISSIONS.OPPORTUNITY_LIST,
                        action: {
                            type: 'navigate',
                            route: '/crm/opportunities',
                        },
                        buttonOrder: 3,
                        tooltip: 'View all opportunities',
                    },
                    {
                        buttonId: 'crm-opportunities-new',
                        label: 'New Opportunity',
                        icon: 'Plus',
                        permission: CRM_PERMISSIONS.OPPORTUNITY_CREATE,
                        action: {
                            type: 'navigate',
                            route: '/crm/opportunities/new',
                        },
                        buttonOrder: 4,
                        tooltip: 'Create a new opportunity',
                    },
                ],
            },
            {
                groupId: 'crm-activities',
                groupLabel: 'Activities',
                groupOrder: 3,
                buttons: [
                    {
                        buttonId: 'crm-activities-list',
                        label: 'Activities',
                        icon: 'Calendar',
                        permission: CRM_PERMISSIONS.ACTIVITY_LIST,
                        action: {
                            type: 'navigate',
                            route: '/crm/activities',
                        },
                        buttonOrder: 1,
                        tooltip: 'View all activities',
                    },
                    {
                        buttonId: 'crm-activities-new',
                        label: 'Log Activity',
                        icon: 'Plus',
                        permission: CRM_PERMISSIONS.ACTIVITY_CREATE,
                        action: {
                            type: 'navigate',
                            route: '/crm/activities/new',
                        },
                        buttonOrder: 2,
                        tooltip: 'Log a new activity',
                    },
                ],
            },
        ],
    },

    routes: [
        // Partners
        {
            routeId: 'crm-partners',
            path: '/crm/partners',
            permission: CRM_PERMISSIONS.PARTNER_LIST,
            component: () => import('./views/PartnersListView'),
        },
        {
            routeId: 'crm-partners-new',
            path: '/crm/partners/new',
            permission: CRM_PERMISSIONS.PARTNER_CREATE,
            component: () => import('./views/PartnerFormView'),
        },
        {
            routeId: 'crm-partners-detail',
            path: '/crm/partners/:id',
            permission: CRM_PERMISSIONS.PARTNER_READ,
            component: () => import('./views/PartnerDetailView'),
        },
        {
            routeId: 'crm-partners-edit',
            path: '/crm/partners/:id/edit',
            permission: CRM_PERMISSIONS.PARTNER_UPDATE,
            component: () => import('./views/PartnerEditView'),
        },

        // Contacts
        {
            routeId: 'crm-contacts',
            path: '/crm/contacts',
            permission: CRM_PERMISSIONS.CONTACT_LIST,
            component: () => import('./views/ContactsListView'),
        },

        // Leads
        {
            routeId: 'crm-leads',
            path: '/crm/leads',
            permission: CRM_PERMISSIONS.LEAD_LIST,
            component: () => import('./views/LeadsListView'),
        },
        {
            routeId: 'crm-leads-new',
            path: '/crm/leads/new',
            permission: CRM_PERMISSIONS.LEAD_CREATE,
            component: () => import('./views/LeadFormView'),
        },

        // Opportunities
        {
            routeId: 'crm-opportunities',
            path: '/crm/opportunities',
            permission: CRM_PERMISSIONS.OPPORTUNITY_LIST,
            component: () => import('./views/OpportunitiesListView'),
        },
        {
            routeId: 'crm-opportunities-new',
            path: '/crm/opportunities/new',
            permission: CRM_PERMISSIONS.OPPORTUNITY_CREATE,
            component: () => import('./views/OpportunityFormView'),
        },

        // Activities
        {
            routeId: 'crm-activities',
            path: '/crm/activities',
            permission: CRM_PERMISSIONS.ACTIVITY_LIST,
            component: () => import('./views/ActivitiesListView'),
        },
    ],

    permissions: getAllCRMPermissions(),
};

export default crmModuleRegistry;
