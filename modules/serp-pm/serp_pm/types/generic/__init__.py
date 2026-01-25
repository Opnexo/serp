"""
Generic project type implementation.

For engineering teams (IIoT, Telecom, hardware/software solutions).
"""

from typing import Any

from serp_pm.domain.entities import Project
from serp_pm.types.interface import IProjectType


class GenericProjectType(IProjectType):
    """Generic project type for engineering teams."""

    @property
    def type_id(self) -> str:
        return "generic"

    @property
    def display_name(self) -> str:
        return "Generic Project"

    @property
    def description(self) -> str:
        return (
            "Traditional project management for engineering teams. "
            "Supports phases, milestones, and deliverables. "
            "Ideal for IIoT, Telecom, and hardware/software solution development."
        )

    def get_ui_config(self) -> dict[str, Any]:
        """Get UI configuration for generic projects."""
        return {
            "views": [
                {
                    "id": "phases",
                    "label": "Phases",
                    "icon": "Layers",
                    "component": "PhaseView",
                },
                {
                    "id": "deliverables",
                    "label": "Deliverables",
                    "icon": "Package",
                    "component": "DeliverableView",
                },
                {
                    "id": "milestones",
                    "label": "Milestones",
                    "icon": "Flag",
                    "component": "MilestoneView",
                },
            ],
            "toolbar": {
                "buttons": [
                    {
                        "id": "add_phase",
                        "label": "Add Phase",
                        "icon": "Plus",
                        "action": "pm.generic.phase.create",
                    },
                    {
                        "id": "add_deliverable",
                        "label": "Add Deliverable",
                        "icon": "PackagePlus",
                        "action": "pm.generic.deliverable.create",
                    },
                ]
            },
        }

    async def on_project_created(self, project: Project) -> None:
        """
        Initialize generic project structure.
        
        Could create default phases like Design, Development, Testing, Deployment.
        """
        # TODO: Create default phases when project is created
        pass

    async def validate_project(self, project: Project) -> list[str]:
        """Validate generic project configuration."""
        errors = []
        
        if not project.name:
            errors.append("Project name is required")
        
        if project.start_date and project.end_date:
            if project.start_date > project.end_date:
                errors.append("Start date must be before end date")
        
        return errors
