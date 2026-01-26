"""
Core domain entities for Project Management module.

These are foundational entities that ALL project management methodologies share.
Methodology-specific modules extend these or add their own entities.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from serp_core.domain.aggregate import AggregateRoot
from serp_core.domain.entity import Entity


@dataclass(kw_only=True)
class Project(AggregateRoot):
    """
    Project aggregate root.

    Core entity representing a project - used by all methodologies.
    Methodology modules can extend this or reference it from their own entities.
    """

    name: str
    project_type: str = "generic"  # Type ID (validated against registry at runtime)
    description: str = ""
    status: str = "PLANNING"  # PLANNING, ACTIVE, ON_HOLD, COMPLETED, CANCELLED
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    owner_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_archived: bool = False

    def start(self) -> None:
        """Start the project."""
        self.status = "ACTIVE"

    def complete(self) -> None:
        """Mark project as completed."""
        self.status = "COMPLETED"

    def put_on_hold(self) -> None:
        """Put project on hold."""
        self.status = "ON_HOLD"

    def cancel(self) -> None:
        """Cancel the project."""
        self.status = "CANCELLED"

    def archive(self) -> None:
        """Archive the project."""
        self.is_archived = True


@dataclass(kw_only=True)
class Task(Entity):
    """
    Generic task/work item entity.

    Foundation for all work items. Methodology modules can:
    - Extend this class (e.g., UserStory(Task) in Scrum)
    - Reference tasks from their own entities
    """

    project_id: UUID
    title: str
    description: str = ""
    status: str = "OPEN"  # OPEN, IN_PROGRESS, DONE, CLOSED
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    assigned_to: Optional[UUID] = None
    parent_id: Optional[UUID] = None  # For subtasks
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    due_date: Optional[date] = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    def assign(self, user_id: UUID) -> None:
        """Assign task to a user."""
        self.assigned_to = user_id

    def start(self) -> None:
        """Start working on the task."""
        self.status = "IN_PROGRESS"

    def complete(self) -> None:
        """Mark task as done."""
        self.status = "DONE"

    def close(self) -> None:
        """Close the task."""
        self.status = "CLOSED"

    def add_tag(self, tag: str) -> None:
        """Add a tag."""
        if tag not in self.tags:
            self.tags.append(tag)


@dataclass(kw_only=True)
class Team(Entity):
    """
    Team entity for project collaboration.

    Represents a group of people working together.
    """

    name: str
    description: str = ""
    project_id: Optional[UUID] = None  # Team can be project-specific or organization-wide
    created_by: Optional[UUID] = None
    is_active: bool = True

    def deactivate(self) -> None:
        """Deactivate the team."""
        self.is_active = False


@dataclass(kw_only=True)
class TeamMember(Entity):
    """
    Team member assignment.

    Links users to teams with specific roles.
    """

    team_id: UUID
    user_id: UUID
    role: str = "MEMBER"  # MEMBER, LEAD, ADMIN
    joined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(kw_only=True)
class Milestone(Entity):
    """
    Project milestone.

    Represents significant points or deliverables in a project timeline.
    """

    project_id: UUID
    name: str
    description: str = ""
    due_date: date
    status: str = "PENDING"  # PENDING, ACHIEVED, MISSED
    created_by: Optional[UUID] = None


@dataclass(kw_only=True)
class Comment(Entity):
    """
    Comment on projects or tasks.

    Enables discussion and collaboration.
    """

    entity_type: str  # "project" or "task"
    entity_id: UUID
    content: str
    author_id: UUID
    parent_id: Optional[UUID] = None  # For threaded comments


@dataclass(kw_only=True)
class Attachment(Entity):
    """
    File attachment linked to projects or tasks.

    References documents from serp-dm module.
    """

    entity_type: str  # "project" or "task"
    entity_id: UUID
    document_id: UUID  # References serp_dm.Document
    uploaded_by: UUID
    description: str = ""
