"""
Project type interface.

All project types (built-in and plugins) must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from serp_pm.domain.entities import Project


class IProjectType(ABC):
    """
    Interface that all project types must implement.
    
    Project types are discovered via entry points in pyproject.toml:
    [project.entry-points."serp.pm.project_types"]
    my_type = "my_package:MyProjectType"
    """

    @property
    @abstractmethod
    def type_id(self) -> str:
        """
        Unique identifier for this project type.
        
        Returns:
            Type ID (e.g., "generic", "kanban", "scrum")
        """
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Human-readable name for this project type.
        
        Returns:
            Display name (e.g., "Generic Project", "Kanban Board")
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Description of this project type and its use cases.
        
        Returns:
            Description text
        """
        pass

    @abstractmethod
    def get_ui_config(self) -> dict[str, Any]:
        """
        Get UI configuration for this project type.
        
        Returns:
            Dictionary with toolbar, views, and other UI config
        """
        pass

    @abstractmethod
    async def on_project_created(self, project: Project) -> None:
        """
        Hook called when a project of this type is created.
        
        Use this to initialize type-specific structures
        (e.g., create default board for Kanban, backlog for Scrum).
        
        Args:
            project: The newly created project
        """
        pass

    @abstractmethod
    async def validate_project(self, project: Project) -> list[str]:
        """
        Validate project configuration for this type.
        
        Args:
            project: Project to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
