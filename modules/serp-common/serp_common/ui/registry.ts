/**
 * Module registry for Common module.
 * Defines ribbon tabs, buttons, and routes.
 */

import type { ModuleRegistry } from '@/types';
import { COMMON_PERMISSIONS, getAllCommonPermissions } from './permissions';

export const commonModuleRegistry: ModuleRegistry = {
    moduleId: 'common',
    moduleName: 'Common',
    version: '0.1.0',
    icon: 'Building',
    description: 'Shared entities and resources',

    ribbon: {
        tabId: 'common',
        tabLabel: 'Common',
        tabIcon: 'Building',
        tabOrder: 5, // Before CRM (10)
        groups: [
            {
                groupId: 'common-resources',
                groupLabel: 'Resources',
                groupOrder: 1,
                buttons: [
                    {
                        buttonId: 'common-addresses-list',
                        label: 'Addresses',
                        icon: 'MapPin',
                        permission: COMMON_PERMISSIONS.ADDRESS_LIST,
                        action: { type: 'navigate', route: '/common/addresses' },
                        buttonOrder: 1,
                        tooltip: 'Manage addresses',
                    },
                ],
            },
        ],
    },

    routes: [
        {
            routeId: 'common-addresses',
            path: '/common/addresses',
            permission: COMMON_PERMISSIONS.ADDRESS_LIST,
            component: () => import('./views/AddressesListView'),
        },
        {
            routeId: 'common-address-detail',
            path: '/common/addresses/:id',
            permission: COMMON_PERMISSIONS.ADDRESS_READ,
            component: () => import('./views/AddressDetailView'),
        },
        {
            routeId: 'common-address-new',
            path: '/common/addresses/new',
            permission: COMMON_PERMISSIONS.ADDRESS_CREATE,
            component: () => import('./views/AddressEditView'),
        },
        {
            routeId: 'common-address-edit',
            path: '/common/addresses/:id/edit',
            permission: COMMON_PERMISSIONS.ADDRESS_UPDATE,
            component: () => import('./views/AddressEditView'),
        },
    ],

    permissions: getAllCommonPermissions(),
};

export default commonModuleRegistry;
