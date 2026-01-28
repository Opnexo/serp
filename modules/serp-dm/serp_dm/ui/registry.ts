import type { ModuleRegistry } from '@/types';
import { DM_PERMISSIONS, getAllDMPermissions } from './permissions';

/**
 * DM Module Registry
 * Defines the module's ribbon tab, buttons, and routes
 */
export const dmModuleRegistry: ModuleRegistry = {
    moduleId: 'dm',
    moduleName: 'Documents',
    version: '0.1.0',
    icon: 'FileText',
    description: 'Document management and version control',

    // HMR configuration for development
    hmr: {
        port: 5174, // Unique port per module
    },

    ribbon: {
        tabId: 'dm',
        tabLabel: 'Documents',
        tabIcon: 'FileText',
        tabOrder: 20,
        groups: [
            {
                groupId: 'dm-documents',
                groupLabel: 'Documents',
                groupOrder: 1,
                buttons: [
                    {
                        buttonId: 'dm-documents-list',
                        label: 'All Documents',
                        icon: 'Files',
                        permission: DM_PERMISSIONS.DOCUMENT_LIST,
                        action: {
                            type: 'navigate',
                            route: '/dm/documents',
                        },
                        buttonOrder: 1,
                        tooltip: 'View all documents',
                    },
                    {
                        buttonId: 'dm-documents-new',
                        label: 'Register',
                        icon: 'FilePlus',
                        permission: DM_PERMISSIONS.DOCUMENT_CREATE,
                        action: {
                            type: 'navigate',
                            route: '/dm/documents/new',
                        },
                        variant: 'primary',
                        buttonOrder: 2,
                        tooltip: 'Register a new document',
                    },
                ],
            },
            {
                groupId: 'dm-kanban',
                groupLabel: 'Workflow',
                groupOrder: 2,
                buttons: [
                    {
                        buttonId: 'dm-kanban',
                        label: 'Kanban',
                        icon: 'Columns',
                        permission: DM_PERMISSIONS.STAGE_LIST,
                        action: {
                            type: 'navigate',
                            route: '/dm/kanban',
                        },
                        buttonOrder: 1,
                        tooltip: 'View Kanban board',
                    },
                ],
            },
            {
                groupId: 'dm-admin',
                groupLabel: 'Admin',
                groupOrder: 3,
                buttons: [
                    {
                        buttonId: 'dm-templates',
                        label: 'Templates',
                        icon: 'LayoutTemplate',
                        permission: DM_PERMISSIONS.TEMPLATE_LIST,
                        action: {
                            type: 'navigate',
                            route: '/dm/admin/templates',
                        },
                        buttonOrder: 1,
                        tooltip: 'Manage storage templates',
                    },
                    {
                        buttonId: 'dm-doctypes',
                        label: 'Doc Types',
                        icon: 'Tag',
                        permission: DM_PERMISSIONS.DOCTYPE_LIST,
                        action: {
                            type: 'navigate',
                            route: '/dm/admin/document-types',
                        },
                        buttonOrder: 2,
                        tooltip: 'Manage document types',
                    },
                ],
            },
        ],
    },

    routes: [
        // Documents
        {
            routeId: 'dm-documents',
            path: '/dm/documents',
            permission: DM_PERMISSIONS.DOCUMENT_LIST,
            component: () => import('./views/DocumentsListView'),
        },
        {
            routeId: 'dm-documents-new',
            path: '/dm/documents/new',
            permission: DM_PERMISSIONS.DOCUMENT_CREATE,
            component: () => import('./views/DocumentFormView'),
        },
        {
            routeId: 'dm-documents-detail',
            path: '/dm/documents/:id',
            permission: DM_PERMISSIONS.DOCUMENT_READ,
            component: () => import('./views/DocumentDetailView'),
        },

        // Kanban
        {
            routeId: 'dm-kanban',
            path: '/dm/kanban',
            permission: DM_PERMISSIONS.STAGE_LIST,
            component: () => import('./views/KanbanBoardView'),
        },

        // Admin
        {
            routeId: 'dm-templates',
            path: '/dm/admin/templates',
            permission: DM_PERMISSIONS.TEMPLATE_LIST,
            component: () => import('./views/TemplatesView'),
        },
        {
            routeId: 'dm-doctypes',
            path: '/dm/admin/document-types',
            permission: DM_PERMISSIONS.DOCTYPE_LIST,
            component: () => import('./views/DocumentTypesView'),
        },
    ],

    permissions: getAllDMPermissions(),

    // Widgets exposed for other modules (PM integration)
    widgets: {
        ProjectDocumentsWidget: () => import('./components/ProjectDocumentsWidget'),
    },
};

export default dmModuleRegistry;
