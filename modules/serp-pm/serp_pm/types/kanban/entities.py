"""
Kanban project type entities.

For continuous flow work with visual boards.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID

from serp_core.domain.entity import Entity


@dataclass
class Board(Entity):
    """
    Kanban board for visualizing work.
    
    One board per Kanban project.
    """

    project_id: UUID
    name: str
    description: str = ""


@dataclass
class Column(Entity):
    """
    Column in a Kanban board.
    
    Represents a workflow stage (e.g., To Do, In Progress, Review, Done).
    """

    board_id: UUID
    name: str
    order: int = 0  # Display order (left to right)
    wip_limit: Optional[int] = None  # Work-in-progress limit
    color: str = "#808080"  # Column color for UI


@dataclass
class Card(Entity):
    """
    Card on a Kanban board.
    
    Represents a work item. Links to a Task entity.
    """

    board_id: UUID
    column_id: UUID
    task_id: UUID  # References serp_pm.domain.entities.Task
    order: int = 0  # Position within column
    blocked: bool = False
    blocked_reason: str = ""


@dataclass
class WIPLimit(Entity):
    """
    Work-in-progress limit rule.
    
    Enforces limits on concurrent work.
    """

    column_id: UUID
    limit: int
    enforce: bool = True  # Whether to enforce (hard limit) or just warn
