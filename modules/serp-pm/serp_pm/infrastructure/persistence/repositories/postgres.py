"""
PostgreSQL repository implementations for Project Management module.
"""

from typing import Optional, Type, TypeVar
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from serp_pm.domain.entities import Project, Task, Team, TeamMember
from serp_pm.domain.repositories import (
    IProjectRepository,
    ITaskRepository,
    ITeamRepository,
)
from serp_pm.infrastructure.persistence.models import (
    ProjectModel,
    TaskModel,
    TeamModel,
)


class PostgresProjectRepository(IProjectRepository):
    """PostgreSQL implementation of Project repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ProjectModel) -> Project:
        """Convert model to entity."""
        return Project(
            id=model.id,
            name=model.name,
            project_type=model.project_type,
            description=model.description,
            status=model.status,
            start_date=model.start_date,
            end_date=model.end_date,
            owner_id=model.owner_id,
            team_id=model.team_id,
            metadata=model.metadata_,
            created_by=model.created_by,
            updated_by=model.updated_by,
            is_archived=model.is_archived,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Project) -> ProjectModel:
        """Convert entity to model."""
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            project_type=entity.project_type,
            description=entity.description,
            status=entity.status,
            start_date=entity.start_date,
            end_date=entity.end_date,
            owner_id=entity.owner_id,
            team_id=entity.team_id,
            metadata_=entity.metadata,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            is_archived=entity.is_archived,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[Project]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: Project) -> Project:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        model = self._to_model(entity)
        await self.session.merge(model)
        await self.session.commit()
        return entity

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def list_all(self) -> list[Project]:
        result = await self.session.execute(select(ProjectModel))
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_owner(self, owner_id: UUID) -> list[Project]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.owner_id == owner_id)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_status(self, status: str) -> list[Project]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.status == status)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    # Aliases
    async def find_by_id(self, entity_id: UUID) -> Optional[Project]:
        return await self.get_by_id(entity_id)

    async def find_all(self) -> list[Project]:
        return await self.list_all()


class PostgresTaskRepository(ITaskRepository):
    """PostgreSQL implementation of Task repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            project_id=model.project_id,
            title=model.title,
            description=model.description,
            status=model.status,
            priority=model.priority,
            assigned_to=model.assigned_to,
            parent_id=model.parent_id,
            estimated_hours=model.estimated_hours,
            actual_hours=model.actual_hours,
            due_date=model.due_date,
            tags=model.tags,
            metadata=model.metadata_,
            created_by=model.created_by,
            updated_by=model.updated_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Task) -> TaskModel:
        return TaskModel(
            id=entity.id,
            project_id=entity.project_id,
            title=entity.title,
            description=entity.description,
            status=entity.status,
            priority=entity.priority,
            assigned_to=entity.assigned_to,
            parent_id=entity.parent_id,
            estimated_hours=entity.estimated_hours,
            actual_hours=entity.actual_hours,
            due_date=entity.due_date,
            tags=entity.tags,
            metadata_=entity.metadata,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[Task]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: Task) -> Task:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        model = self._to_model(entity)
        await self.session.merge(model)
        await self.session.commit()
        return entity

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def list_all(self) -> list[Task]:
        result = await self.session.execute(select(TaskModel))
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_project(self, project_id: UUID) -> list[Task]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.project_id == project_id)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_assignee(self, user_id: UUID) -> list[Task]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.assigned_to == user_id)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_status(self, status: str) -> list[Task]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.status == status)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    # Aliases
    async def find_by_id(self, entity_id: UUID) -> Optional[Task]:
        return await self.get_by_id(entity_id)

    async def find_all(self) -> list[Task]:
        return await self.list_all()


class PostgresTeamRepository(ITeamRepository):
    """PostgreSQL implementation of Team repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: TeamModel) -> Team:
        return Team(
            id=model.id,
            name=model.name,
            description=model.description,
            project_id=model.project_id,
            created_by=model.created_by,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Team) -> TeamModel:
        return TeamModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            project_id=entity.project_id,
            created_by=entity.created_by,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[Team]:
        result = await self.session.execute(
            select(TeamModel).where(TeamModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: Team) -> Team:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        model = self._to_model(entity)
        await self.session.merge(model)
        await self.session.commit()
        return entity

    async def delete(self, id: UUID) -> None:
        result = await self.session.execute(
            select(TeamModel).where(TeamModel.id == id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def list_all(self) -> list[Team]:
        result = await self.session.execute(select(TeamModel))
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_by_project(self, project_id: UUID) -> Optional[Team]:
        result = await self.session.execute(
            select(TeamModel).where(TeamModel.project_id == project_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    # Aliases
    async def find_by_id(self, entity_id: UUID) -> Optional[Team]:
        return await self.get_by_id(entity_id)

    async def find_all(self) -> list[Team]:
        return await self.list_all()
