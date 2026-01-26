import type { ModuleRegistry } from '@/types';
import { PM_PERMISSIONS, getAllPMPermissions } from './permissions';

/**
 * PM Module Registry
 * Defines the module's ribbon tab, buttons, and routes
 */
export const pmModuleRegistry: ModuleRegistry = {
    moduleId: 'pm',
    moduleName: 'Project Management',
    version: '0.1.0',
    icon: 'Briefcase',
    description: 'Project and task management',

    // HMR configuration for development
    hmr: {
        port: 5173, // Unique port per module
    },

    ribbon: {
        tabId: 'pm',
        tabLabel: 'Projects',
        tabIcon: 'Briefcase',
        tabOrder: 15,
        groups: [
            {
                groupId: 'pm-projects',
                groupLabel: 'Projects',
                groupOrder: 1,
                buttons: [
                    {
                        buttonId: 'pm-projects-list',
                        label: 'All Projects',
                        icon: 'List',
                        permission: PM_PERMISSIONS.PROJECT_LIST,
                        action: {
                            type: 'navigate',
                            route: '/pm/projects',
                        },
                        buttonOrder: 1,
                        tooltip: 'View all projects',
                    },
                    {
                        buttonId: 'pm-projects-new',
                        label: 'New Project',
                        icon: 'FolderPlus',
                        permission: PM_PERMISSIONS.PROJECT_CREATE,
                        action: {
                            type: 'navigate',
                            route: '/pm/projects/new',
                        },
                        variant: 'primary',
                        buttonOrder: 2,
                        tooltip: 'Create a new project',
                    },
                ],
            },
            {
                groupId: 'pm-tasks',
                groupLabel: 'Tasks',
                groupOrder: 2,
                buttons: [
                    {
                        buttonId: 'pm-tasks-list',
                        label: 'All Tasks',
                        icon: 'CheckSquare',
                        permission: PM_PERMISSIONS.TASK_LIST,
                        action: {
                            type: 'navigate',
                            route: '/pm/tasks',
                        },
                        buttonOrder: 1,
                        tooltip: 'View all tasks',
                    },
                    {
                        buttonId: 'pm-tasks-new',
                        label: 'New Task',
                        icon: 'Plus',
                        permission: PM_PERMISSIONS.TASK_CREATE,
                        action: {
                            type: 'navigate',
                            route: '/pm/tasks/new',
                        },
                        buttonOrder: 2,
                        tooltip: 'Create a new task',
                    },
                ],
            },
        ],
    },

    routes: [
        // Projects
        {
            routeId: 'pm-projects',
            path: '/pm/projects',
            permission: PM_PERMISSIONS.PROJECT_LIST,
            component: () => import('./views/ProjectsListView'),
        },
        // {
        //     routeId: 'pm-projects-new',
        //     path: '/pm/projects/new',
        //     permission: PM_PERMISSIONS.PROJECT_CREATE,
        //     component: () => import('./views/ProjectFormView'),
        // },
        // {
        //     routeId: 'pm-projects-detail',
        //     path: '/pm/projects/:id',
        //     permission: PM_PERMISSIONS.PROJECT_READ,
        //     component: () => import('./views/ProjectDetailView'),
        // },

        // // Tasks
        // {
        //     routeId: 'pm-tasks',
        //     path: '/pm/tasks',
        //     permission: PM_PERMISSIONS.TASK_LIST,
        //     component: () => import('./views/TasksListView'),
        // },
    ],

    permissions: getAllPMPermissions(),
};

export default pmModuleRegistry;
