"""In-memory repository implementations for testing."""

from typing import Optional
from uuid import UUID, uuid4

from serp_pm.domain.entities import Project, Task, Team
from serp_pm.domain.repositories import IProjectRepository, ITaskRepository, ITeamRepository


class InMemoryProjectRepository(IProjectRepository):
    """In-memory project repository."""

    def __init__(self):
        self._projects: dict[UUID, Project] = {}

    async def get_by_id(self, id: UUID) -> Optional[Project]:
        return self._projects.get(id)

    async def save(self, entity: Project) -> Project:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        self._projects[entity.id] = entity
        return entity

    async def delete(self, id: UUID) -> None:
        self._projects.pop(id, None)

    async def list_all(self) -> list[Project]:
        return list(self._projects.values())

    async def find_by_owner(self, owner_id: UUID) -> list[Project]:
        return [p for p in self._projects.values() if p.owner_id == owner_id]

    async def find_by_status(self, status: str) -> list[Project]:
        return [p for p in self._projects.values() if p.status == status]


class InMemoryTaskRepository(ITaskRepository):
    """In-memory task repository."""

    def __init__(self):
        self._tasks: dict[UUID, Task] = {}

    async def get_by_id(self, id: UUID) -> Optional[Task]:
        return self._tasks.get(id)

    async def save(self, entity: Task) -> Task:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        self._tasks[entity.id] = entity
        return entity

    async def delete(self, id: UUID) -> None:
        self._tasks.pop(id, None)

    async def list_all(self) -> list[Task]:
        return list(self._tasks.values())

    async def find_by_project(self, project_id: UUID) -> list[Task]:
        return [t for t in self._tasks.values() if t.project_id == project_id]

    async def find_by_assignee(self, user_id: UUID) -> list[Task]:
        return [t for t in self._tasks.values() if t.assigned_to == user_id]

    async def find_by_status(self, status: str) -> list[Task]:
        return [t for t in self._tasks.values() if t.status == status]


class InMemoryTeamRepository(ITeamRepository):
    """In-memory team repository."""

    def __init__(self):
        self._teams: dict[UUID, Team] = {}

    async def get_by_id(self, id: UUID) -> Optional[Team]:
        return self._teams.get(id)

    async def save(self, entity: Team) -> Team:
        if entity.id == UUID(int=0):
            entity.id = uuid4()
        self._teams[entity.id] = entity
        return entity

    async def delete(self, id: UUID) -> None:
        self._teams.pop(id, None)

    async def list_all(self) -> list[Team]:
        return list(self._teams.values())

    async def find_by_project(self, project_id: UUID) -> Optional[Team]:
        for team in self._teams.values():
            if team.project_id == project_id:
                return team
        return None
