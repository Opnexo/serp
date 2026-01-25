"""
Kanban project type implementation.

For continuous flow work with visual boards.
"""

from typing import Any

from serp_pm.domain.entities import Project
from serp_pm.types.interface import IProjectType


class KanbanProjectType(IProjectType):
    """Kanban project type for continuous flow work."""

    @property
    def type_id(self) -> str:
        return "kanban"

    @property
    def display_name(self) -> str:
        return "Kanban Board"

    @property
    def description(self) -> str:
        return (
            "Visual workflow management with Kanban boards. "
            "Continuous flow, WIP limits, and pull-based system. "
            "Ideal for operations, support, and continuous delivery teams."
        )

    def get_ui_config(self) -> dict[str, Any]:
        """Get UI configuration for Kanban projects."""
        return {
            "views": [
                {
                    "id": "board",
                    "label": "Board",
                    "icon": "Kanban",
                    "component": "KanbanBoardView",
                    "default": True,
                },
                {
                    "id": "metrics",
                    "label": "Flow Metrics",
                    "icon": "TrendingUp",
                    "component": "KanbanMetricsView",
                },
            ],
            "toolbar": {
                "buttons": [
                    {
                        "id": "add_card",
                        "label": "Add Card",
                        "icon": "Plus",
                        "action": "pm.kanban.card.create",
                    },
                    {
                        "id": "configure_columns",
                        "label": "Configure Columns",
                        "icon": "Settings",
                        "action": "pm.kanban.columns.configure",
                    },
                ]
            },
        }

    async def on_project_created(self, project: Project) -> None:
        """
        Initialize Kanban board structure.
        
        Creates default board with basic columns:
        - Backlog
        - To Do
        - In Progress
        - Review
        - Done
        """
        # TODO: Create default board and columns
        pass

    async def validate_project(self, project: Project) -> list[str]:
        """Validate Kanban project configuration."""
        errors = []
        
        if not project.name:
            errors.append("Project name is required")
        
        # Kanban projects don't typically have end dates
        # They're continuous flow
        
        return errors
