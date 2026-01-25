"""
Domain events for Project Management module.

These events are published by the core PM module and can be subscribed to
by methodology extension modules.
"""

from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from serp_core.events.domain.base_event import DomainEvent


# Project Events
@dataclass
class ProjectCreatedEvent(DomainEvent):
    """Event raised when a project is created."""

    project_id: UUID
    name: str
    owner_id: Optional[UUID]
    created_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.project.created"


@dataclass
class ProjectUpdatedEvent(DomainEvent):
    """Event raised when a project is updated."""

    project_id: UUID
    name: str
    updated_by: Optional[UUID]
    changes: dict[str, Any]

    @property
    def event_type(self) -> str:
        return "pm.project.updated"


@dataclass
class ProjectStatusChangedEvent(DomainEvent):
    """Event raised when project status changes."""

    project_id: UUID
    old_status: str
    new_status: str
    changed_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.project.status_changed"


@dataclass
class ProjectCompletedEvent(DomainEvent):
    """Event raised when a project is completed."""

    project_id: UUID
    name: str
    completed_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.project.completed"


# Task Events
@dataclass
class TaskCreatedEvent(DomainEvent):
    """Event raised when a task is created."""

    task_id: UUID
    project_id: UUID
    title: str
    created_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.task.created"


@dataclass
class TaskUpdatedEvent(DomainEvent):
    """Event raised when a task is updated."""

    task_id: UUID
    title: str
    updated_by: Optional[UUID]
    changes: dict[str, Any]

    @property
    def event_type(self) -> str:
        return "pm.task.updated"


@dataclass
class TaskStatusChangedEvent(DomainEvent):
    """Event raised when task status changes."""

    task_id: UUID
    project_id: UUID
    old_status: str
    new_status: str
    changed_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.task.status_changed"


@dataclass
class TaskAssignedEvent(DomainEvent):
    """Event raised when a task is assigned."""

    task_id: UUID
    project_id: UUID
    assigned_to: UUID
    assigned_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.task.assigned"


@dataclass
class TaskCompletedEvent(DomainEvent):
    """Event raised when a task is completed."""

    task_id: UUID
    project_id: UUID
    completed_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.task.completed"


# Team Events
@dataclass
class TeamCreatedEvent(DomainEvent):
    """Event raised when a team is created."""

    team_id: UUID
    name: str
    created_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.team.created"


@dataclass
class TeamMemberAddedEvent(DomainEvent):
    """Event raised when a member is added to a team."""

    team_id: UUID
    user_id: UUID
    role: str
    added_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.team.member_added"


@dataclass
class TeamMemberRemovedEvent(DomainEvent):
    """Event raised when a member is removed from a team."""

    team_id: UUID
    user_id: UUID
    removed_by: Optional[UUID]

    @property
    def event_type(self) -> str:
        return "pm.team.member_removed"


# Milestone Events
@dataclass
class MilestoneReachedEvent(DomainEvent):
    """Event raised when a milestone is achieved."""

    milestone_id: UUID
    project_id: UUID
    name: str

    @property
    def event_type(self) -> str:
        return "pm.milestone.reached"
