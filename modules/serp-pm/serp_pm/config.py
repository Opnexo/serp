"""
Configuration settings for Project Management module.
"""

from pydantic_settings import BaseSettings


class PMSettings(BaseSettings):
    """Project Management module settings."""

    # Module metadata
    module_name: str = "Project Management"
    module_version: str = "0.1.0"

    # Database configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/serp"
    database_schema: str = "pm"  # PostgreSQL schema for this module
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Feature flags
    enable_task_dependencies: bool = True
    enable_time_tracking: bool = True
    enable_comments: bool = True
    enable_attachments: bool = True

    # Task settings
    default_task_status: str = "OPEN"
    default_priority: str = "MEDIUM"
    max_task_nesting_level: int = 5  # For subtasks

    # Project settings
    default_project_status: str = "PLANNING"
    allow_project_templates: bool = True

    # Team settings
    max_team_size: int = 100

    # Time tracking
    time_estimate_unit: str = "hours"  # hours, story_points, days
    track_actual_time: bool = True

    class Config:
        """Pydantic config."""

        env_prefix = "SERP_PM_"
        case_sensitive = False
