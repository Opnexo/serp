"""
Scrum project type entities.

For sprint-based iterative development.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional
from uuid import UUID

from serp_core.domain.entity import Entity
from serp_pm.domain.entities import Task


@dataclass
class Sprint(Entity):
    """
    Scrum sprint - time-boxed iteration.
    
    Typically 2-4 weeks long.
    """

    project_id: UUID
    name: str
    goal: str = ""
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=date.today)
    status: str = "PLANNED"  # PLANNED, ACTIVE, COMPLETED


@dataclass
class UserStory(Task):
    """
    User story - extends base Task with Scrum-specific fields.
    
    Format: "As a [user], I want [feature] so that [benefit]"
    """

    story_points: Optional[int] = None  # Estimation in story points
    sprint_id: Optional[UUID] = None  # Current sprint
    acceptance_criteria: list[str] = field(default_factory=list)
    epic_id: Optional[UUID] = None  # Parent epic


@dataclass
class ProductBacklog(Entity):
    """
    Product backlog - prioritized list of work.
    
    One backlog per Scrum project.
    """

    project_id: UUID
    name: str = "Product Backlog"
    description: str = ""


@dataclass
class BacklogItem(Entity):
    """
    Item in the product backlog.
    
    Links to UserStory or Task.
    """

    backlog_id: UUID
    story_id: UUID  # References UserStory
    priority: int = 0  # Lower number = higher priority
    order: int = 0  # Display order


@dataclass
class SprintVelocity(Entity):
    """
    Team velocity tracking per sprint.
    
    Measures story points completed.
    """

    sprint_id: UUID
    planned_points: int = 0
    completed_points: int = 0
    carried_over_points: int = 0
