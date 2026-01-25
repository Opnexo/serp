"""
Project type registry.

Discovers and manages project types via Python entry points.
"""

import logging
from typing import Optional

try:
    from importlib.metadata import entry_points
except ImportError:
    from importlib_metadata import entry_points  # Python < 3.8

from serp_pm.types.interface import IProjectType

logger = logging.getLogger(__name__)


class ProjectTypeRegistry:
    """
    Registry for discovering and managing project types.
    
    Project types are discovered via entry points:
    [project.entry-points."serp.pm.project_types"]
    my_type = "my_package:MyProjectType"
    """

    _types: dict[str, IProjectType] = {}
    _discovered: bool = False

    @classmethod
    def discover(cls) -> None:
        """
        Discover project types from entry points.
        
        Scans the "serp.pm.project_types" entry point group and loads
        all registered project types.
        """
        if cls._discovered:
            logger.debug("Project types already discovered")
            return

        logger.info("Discovering project types...")
        cls._types.clear()

        try:
            # Python 3.10+ syntax
            eps = entry_points(group="serp.pm.project_types")
        except TypeError:
            # Python 3.9 syntax
            eps = entry_points().get("serp.pm.project_types", [])

        for ep in eps:
            try:
                # Load the entry point (class)
                project_type_class = ep.load()
                
                # Instantiate it
                project_type = project_type_class()
                
                # Validate it implements the interface
                if not isinstance(project_type, IProjectType):
                    logger.error(
                        f"Project type '{ep.name}' does not implement IProjectType"
                    )
                    continue

                # Register it
                type_id = project_type.type_id
                if type_id in cls._types:
                    logger.warning(
                        f"Project type '{type_id}' already registered, skipping '{ep.name}'"
                    )
                    continue

                cls._types[type_id] = project_type
                logger.info(
                    f"Registered project type: {type_id} ({project_type.display_name})"
                )

            except Exception as e:
                logger.error(f"Failed to load project type '{ep.name}': {e}")
                continue

        cls._discovered = True
        logger.info(f"Discovered {len(cls._types)} project type(s)")

    @classmethod
    def get(cls, type_id: str) -> Optional[IProjectType]:
        """
        Get a project type by ID.
        
        Args:
            type_id: Type identifier (e.g., "generic", "kanban")
            
        Returns:
            Project type instance or None if not found
        """
        if not cls._discovered:
            cls.discover()
        return cls._types.get(type_id)

    @classmethod
    def all_types(cls) -> list[IProjectType]:
        """
        Get all registered project types.
        
        Returns:
            List of all project type instances
        """
        if not cls._discovered:
            cls.discover()
        return list(cls._types.values())

    @classmethod
    def get_type_ids(cls) -> list[str]:
        """
        Get all registered project type IDs.
        
        Returns:
            List of type IDs
        """
        if not cls._discovered:
            cls.discover()
        return list(cls._types.keys())

    @classmethod
    def is_valid_type(cls, type_id: str) -> bool:
        """
        Check if a type ID is valid/registered.
        
        Args:
            type_id: Type identifier to check
            
        Returns:
            True if type is registered
        """
        if not cls._discovered:
            cls.discover()
        return type_id in cls._types

    @classmethod
    def reset(cls) -> None:
        """Reset the registry (mainly for testing)."""
        cls._types.clear()
        cls._discovered = False
