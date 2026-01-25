"""UIconfiguration for Project Management module."""

from typing import Any


def load_ui_config() -> dict[str, Any]:
    """Load UI configuration for PM module."""
    return {
        "module_id": "pm",
        "module_name": "Project Management",
        "toolbar": {
            "tabs": [
                {
                    "id": "projects",
                    "label": "Projects",
                    "icon": "Briefcase",
                    "groups": [
                        {
                            "id": "new",
                            "label": "New",
                            "buttons": [
                                {"id": "new_project", "label": "New Project", "icon": "Plus", "action": "pm.project.create", "permission": "pm.project.create"},
                                {"id": "new_task", "label": "New Task", "icon": "CheckSquare", "action": "pm.task.create", "permission": "pm.task.create"},
                            ],
                        },
                    ],
                }
            ],
        },
        "routes": [
            {"path": "/pm/projects", "name": "Projects", "component": "ProjectList", "permission": "pm.project.list"},
            {"path": "/pm/tasks", "name": "Tasks", "component": "TaskList", "permission": "pm.task.list"},
        ],
        "navigation": [
            {"label": "Projects", "icon": "Briefcase", "path": "/pm/projects", "permission": "pm.project.list"},
        ],
    }
