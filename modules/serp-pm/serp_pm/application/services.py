"""Application services for Project Management module."""

from typing import Optional
from uuid import UUID

from serp_core.application.service import ApplicationService

from serp_pm.application.dto import (
    CreateProjectRequest,
    CreateTaskRequest,
    CreateTeamRequest,
    ProjectDTO,
    TaskDTO,
    TeamDTO,
    UpdateProjectRequest,
    UpdateTaskRequest,
)
from serp_pm.domain.entities import Project, Task, Team
from serp_pm.domain.repositories import IProjectRepository, ITaskRepository, ITeamRepository


class ProjectService(ApplicationService):
    """Application service for project management."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def create_project(
        self, request: CreateProjectRequest, created_by: Optional[UUID] = None
    ) ->ProjectDTO:
        """Create a new project."""
        from serp_pm.types.registry import ProjectTypeRegistry
        
        # Validate project type
        if hasattr(request, 'project_type') and request.project_type:
            if not ProjectTypeRegistry.is_valid_type(request.project_type):
                valid_types = ProjectTypeRegistry.get_type_ids()
                raise ValueError(
                    f"Invalid project type '{request.project_type}'. "
                    f"Valid types: {', '.join(valid_types)}"
                )
            project_type = request.project_type
        else:
            project_type = "generic"  # Default type
        
        project = Project(
            id=UUID(int=0),
            name=request.name,
            project_type=project_type,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            owner_id=request.owner_id,
            team_id=request.team_id,
            created_by=created_by,
        )
        saved = await self.project_repository.save(project)
        
        # Call project type hook
        pt = ProjectTypeRegistry.get(project_type)
        if pt:
            await pt.on_project_created(saved)
        
        return self._to_dto(saved)

    async def get_project(self, project_id: UUID) -> Optional[ProjectDTO]:
        """Get project by ID."""
        project = await self.project_repository.get_by_id(project_id)
        return self._to_dto(project) if project else None

    def _to_dto(self, project: Project) -> ProjectDTO:
        """Convert to DTO."""
        return ProjectDTO(
            id=project.id,
            name=project.name,
            project_type=project.project_type,
            description=project.description,
            status=project.status,
            start_date=project.start_date,
            end_date=project.end_date,
            owner_id=project.owner_id,
            team_id=project.team_id,
            is_archived=project.is_archived,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )


class TaskService(ApplicationService):
    """Application service for task management."""

    def __init__(self, task_repository: ITaskRepository):
        self.task_repository = task_repository

    async def create_task(
        self, request: CreateTaskRequest, created_by: Optional[UUID] = None
    ) -> TaskDTO:
        """Create a new task."""
        task = Task(
            id=UUID(int=0),
            project_id=request.project_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            assigned_to=request.assigned_to,
            parent_id=request.parent_id,
            estimated_hours=request.estimated_hours,
            due_date=request.due_date,
            created_by=created_by,
        )
        saved = await self.task_repository.save(task)
        return self._to_dto(saved)

    async def get_task(self, task_id: UUID) -> Optional[TaskDTO]:
        """Get task by ID."""
        task = await self.task_repository.get_by_id(task_id)
        return self._to_dto(task) if task else None

    def _to_dto(self, task: Task) -> TaskDTO:
        """Convert to DTO."""
        return TaskDTO(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assigned_to=task.assigned_to,
            parent_id=task.parent_id,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours,
            due_date=task.due_date,
            tags=task.tags,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class TeamService(ApplicationService):
    """Application service for team management."""

    def __init__(self, team_repository: ITeamRepository):
        self.team_repository = team_repository

    async def create_team(
        self, request: CreateTeamRequest, created_by: Optional[UUID] = None
    ) -> TeamDTO:
        """Create a new team."""
        team = Team(
            id=UUID(int=0),
            name=request.name,
            description=request.description,
            project_id=request.project_id,
            created_by=created_by,
        )
        saved = await self.team_repository.save(team)
        return self._to_dto(saved)

    def _to_dto(self, team: Team) -> TeamDTO:
        """Convert to DTO."""
        return TeamDTO(
            id=team.id,
            name=team.name,
            description=team.description,
            project_id=team.project_id,
            is_active=team.is_active,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )
