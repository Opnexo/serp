"""Data Transfer Objects for Project Management module."""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Project DTOs
class CreateProjectRequest(BaseModel):
    """Request to create a project."""
    name: str = Field(..., min_length=1, max_length=255)
    project_type: str = "generic"  # Type ID (generic, kanban, scrum, or custom)
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    owner_id: Optional[UUID] = None
    team_id: Optional[UUID] = None


class UpdateProjectRequest(BaseModel):
    """Request to update a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectDTO(BaseModel):
    """Project data transfer object."""
    id: UUID
    name: str
    project_type: str
    description: str
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    owner_id: Optional[UUID]
    team_id: Optional[UUID]
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Task DTOs
class CreateTaskRequest(BaseModel):
    """Request to create a task."""
    project_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    priority: str = "MEDIUM"
    assigned_to: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    estimated_hours: Optional[float] = None
    due_date: Optional[date] = None


class UpdateTaskRequest(BaseModel):
    """Request to update a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None
    estimated_hours: Optional[float] = None
    due_date: Optional[date] = None


class TaskDTO(BaseModel):
    """Task data transfer object."""
    id: UUID
    project_id: UUID
    title: str
    description: str
    status: str
    priority: str
    assigned_to: Optional[UUID]
    parent_id: Optional[UUID]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    due_date: Optional[date]
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Team DTOs
class CreateTeamRequest(BaseModel):
    """Request to create a team."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    project_id: Optional[UUID] = None


class TeamDTO(BaseModel):
    """Team data transfer object."""
    id: UUID
    name: str
    description: str
    project_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# List/Pagination Response DTOs
class ProjectListResponse(BaseModel):
    """Paginated list of projects."""
    items: list[ProjectDTO]
    total: int
    page: int = 1
    page_size: int = 50


class TaskListResponse(BaseModel):
    """Paginated list of tasks."""
    items: list[TaskDTO]
    total: int
    page: int = 1
    page_size: int = 50
