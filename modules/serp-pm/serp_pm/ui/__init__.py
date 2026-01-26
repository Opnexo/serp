"""UI configuration for Project Management module."""

from typing import Any


def load_ui_config() -> dict[str, Any]:
    """
    Load UI configuration for PM module.
    
    This configuration is discovered by the shell via entry points
    and used to dynamically configure:
    - Ribbon toolbar tabs and buttons
    - Routes with their component mappings
    - Module permissions
    - HMR config for development
    """
    return {
        "moduleId": "pm",
        "moduleName": "Project Management",
        "version": "0.1.0",
        "icon": "Briefcase",
        "description": "Project and task management",
        # HMR configuration for development hot reload
        "hmr": {
            "port": 5173,
        },
        "ribbon": {
            "tabId": "pm",
            "tabLabel": "Projects",
            "tabIcon": "Briefcase",
            "tabOrder": 15,
            "groups": [
                {
                    "groupId": "pm-projects",
                    "groupLabel": "Projects",
                    "groupOrder": 1,
                    "buttons": [
                        {
                            "buttonId": "pm-projects-list",
                            "label": "All Projects",
                            "icon": "List",
                            "action": {
                                "type": "navigate",
                                "route": "/pm/projects",
                            },
                            "buttonOrder": 1,
                            "tooltip": "View all projects",
                        },
                        {
                            "buttonId": "pm-projects-new",
                            "label": "New Project",
                            "icon": "FolderPlus",
                            "action": {
                                "type": "navigate",
                                "route": "/pm/projects/new",
                            },
                            "variant": "primary",
                            "buttonOrder": 2,
                            "tooltip": "Create a new project",
                        },
                    ],
                },
                {
                    "groupId": "pm-tasks",
                    "groupLabel": "Tasks",
                    "groupOrder": 2,
                    "buttons": [
                        {
                            "buttonId": "pm-tasks-list",
                            "label": "All Tasks",
                            "icon": "CheckSquare",
                            "action": {
                                "type": "navigate",
                                "route": "/pm/tasks",
                            },
                            "buttonOrder": 1,
                            "tooltip": "View all tasks",
                        },
                        {
                            "buttonId": "pm-tasks-new",
                            "label": "New Task",
                            "icon": "Plus",
                            "action": {
                                "type": "navigate",
                                "route": "/pm/tasks/new",
                            },
                            "buttonOrder": 2,
                            "tooltip": "Create a new task",
                        },
                    ],
                },
            ],
        },
        "routes": [
            {
                "routeId": "pm-projects",
                "path": "/pm/projects",
                "component": "ProjectsListView",
            },
            {
                "routeId": "pm-projects-new",
                "path": "/pm/projects/new",
                "component": "ProjectFormView",
            },
            {
                "routeId": "pm-projects-detail",
                "path": "/pm/projects/:id",
                "component": "ProjectDetailView",
            },
            {
                "routeId": "pm-tasks",
                "path": "/pm/tasks",
                "component": "TasksListView",
            },
        ],
        "permissions": [
            "pm.project.list",
            "pm.project.read",
            "pm.project.create",
            "pm.project.update",
            "pm.project.delete",
            "pm.task.list",
            "pm.task.read",
            "pm.task.create",
            "pm.task.update",
            "pm.task.delete",
        ],
    }
