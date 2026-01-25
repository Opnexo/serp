"""FastAPI routes for Project Management module."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from serp_pm.application.dto import (
    CreateProjectRequest,
    CreateTaskRequest,
    ProjectDTO,
    ProjectListResponse,
    TaskDTO,
    TaskListResponse,
)
from serp_pm.application.services import ProjectService, TaskService

router = APIRouter()


# Simplified dependency (use proper DI in production)
def get_project_service() -> ProjectService:
    from serp_pm.infrastructure.persistence.repositories.memory import InMemoryProjectRepository
    return ProjectService(InMemoryProjectRepository())


def get_task_service() -> TaskService:
    from serp_pm.infrastructure.persistence.repositories.memory import InMemoryTaskRepository
    return TaskService(InMemoryTaskRepository())


# Project routes
@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    page: int = 1,
    page_size: int = 50,
    service: ProjectService = Depends(get_project_service),
):
    """List all projects."""
    # Simplified - no pagination
    projects = await service.project_repository.list_all()
    project_dtos = [service._to_dto(p) for p in projects]
    return ProjectListResponse(items=project_dtos, total=len(project_dtos), page=page, page_size=page_size)


@router.get("/projects/{project_id}", response_model=ProjectDTO)
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
):
    """Get project by ID."""
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/projects", response_model=ProjectDTO, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    service: ProjectService = Depends(get_project_service),
):
    """Create a new project."""
    return await service.create_project(request)


# Task routes
@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    project_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 50,
    service: TaskService = Depends(get_task_service),
):
    """List all tasks."""
    if project_id:
        tasks = await service.task_repository.find_by_project(project_id)
    else:
        tasks = await service.task_repository.list_all()
    task_dtos = [service._to_dto(t) for t in tasks]
    return TaskListResponse(items=task_dtos, total=len(task_dtos), page=page, page_size=page_size)


@router.post("/tasks", response_model=TaskDTO, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    service: TaskService = Depends(get_task_service),
):
    """Create a new task."""
    return await service.create_task(request)


@router.get("/project-types")
async def list_project_types():
    """
    List all available project types.
    
    Returns information about registered project types from entry points.
    """
    from serp_pm.types.registry import ProjectTypeRegistry
    
    # Ensure types are discovered
    ProjectTypeRegistry.discover()
    
    types = ProjectTypeRegistry.all_types()
    return {
        "project_types": [
            {
                "type_id": pt.type_id,
                "display_name": pt.display_name,
                "description": pt.description,
                "ui_config": pt.get_ui_config(),
            }
            for pt in types
        ]
    }


def load_api_routes() -> APIRouter:
    """Entry point for loading API routes."""
    return router
