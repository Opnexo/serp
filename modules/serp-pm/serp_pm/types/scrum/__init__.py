"""
Scrum project type implementation.

For sprint-based iterative development.
"""

from typing import Any

from serp_pm.domain.entities import Project
from serp_pm.types.interface import IProjectType


class ScrumProjectType(IProjectType):
    """Scrum project type for sprint-based development."""

    @property
    def type_id(self) -> str:
        return "scrum"

    @property
    def display_name(self) -> str:
        return "Scrum Project"

    @property
    def description(self) -> str:
        return (
            "Agile iterative development with sprints. "
            "Time-boxed iterations, user stories, story points, and velocity tracking. "
            "Ideal for software development and product teams."
        )

    def get_ui_config(self) -> dict[str, Any]:
        """Get UI configuration for Scrum projects."""
        return {
            "views": [
                {
                    "id": "backlog",
                    "label": "Product Backlog",
                    "icon": "List",
                    "component": "BacklogView",
                    "default": True,
                },
                {
                    "id": "sprint",
                    "label": "Active Sprint",
                    "icon": "Zap",
                    "component": "SprintView",
                },
                {
                    "id": "sprint_planning",
                    "label": "Sprint Planning",
                    "icon": "Calendar",
                    "component": "SprintPlanningView",
                },
                {
                    "id": "velocity",
                    "label": "Velocity",
                    "icon": "TrendingUp",
                    "component": "VelocityChartView",
                },
            ],
            "toolbar": {
                "buttons": [
                    {
                        "id": "add_story",
                        "label": "Add Story",
                        "icon": "Plus",
                        "action": "pm.scrum.story.create",
                    },
                    {
                        "id": "start_sprint",
                        "label": "Start Sprint",
                        "icon": "Play",
                        "action": "pm.scrum.sprint.start",
                    },
                    {
                        "id": "planning_poker",
                        "label": "Planning Poker",
                        "icon": "Users",
                        "action": "pm.scrum.planning_poker",
                    },
                ]
            },
        }

    async def on_project_created(self, project: Project) -> None:
        """
        Initialize Scrum project structure.
        
        Creates:
        - Product backlog
        - First sprint (planned state)
        """
        # TODO: Create product backlog and initial sprint
        pass

    async def validate_project(self, project: Project) -> list[str]:
        """Validate Scrum project configuration."""
        errors = []
        
        if not project.name:
            errors.append("Project name is required")
        
        # Scrum projects should have a team
        if not project.team_id:
            errors.append("Scrum projects require a team")
        
        return errors
