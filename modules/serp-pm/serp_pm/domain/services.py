"""Domain services for Project Management module."""

from typing import Optionalfrom uuid import UUID

from serp_pm.domain.entities import Project, Task


class ProjectDomainService:
    """Domain service for project business logic."""

    @staticmethod
    def can_complete_project(project: Project, open_tasks_count: int) -> bool:
        """Check if project can be completed."""
        return open_tasks_count == 0

    @staticmethod
    def calculate_progress(total_tasks: int, completed_tasks: int) -> float:
        """Calculate project progress percentage."""
        if total_tasks == 0:
            return 0.0
        return (completed_tasks / total_tasks) * 100


class TaskDomainService:
    """Domain service for task business logic."""

    @staticmethod
    def can_assign_task(task: Task, user_id: UUID) -> bool:
        """Check if task can be assigned to user."""
        # Add business rules here
        return True

    @staticmethod
    def calculate_total_estimate(tasks: list[Task]) -> float:
        """Calculate total estimated hours for tasks."""
        return sum(t.estimated_hours or 0 for t in tasks)
