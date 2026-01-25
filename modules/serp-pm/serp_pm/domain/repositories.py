"""
Repository interfaces for Project Management module.
"""

from abc import abstractmethod
from typing import Optional
from uuid import UUID

from serp_core.domain.repository import IRepository

from serp_pm.domain.entities import (
    Attachment,
    Comment,
    Milestone,
    Project,
    Task,
    Team,
    TeamMember,
)


class IProjectRepository(IRepository[Project]):
    """Project repository interface."""

    @abstractmethod
    async def find_by_owner(self, owner_id: UUID) -> list[Project]:
        """Find projects by owner."""
        pass

    @abstractmethod
    async def find_by_status(self, status: str) -> list[Project]:
        """Find projects by status."""
        pass


class ITaskRepository(IRepository[Task]):
    """Task repository interface."""

    @abstractmethod
    async def find_by_project(self, project_id: UUID) -> list[Task]:
        """Find all tasks in a project."""
        pass

    @abstractmethod
    async def find_by_assignee(self, user_id: UUID) -> list[Task]:
        """Find tasks assigned to a user."""
        pass

    @abstractmethod
    async def find_by_status(self, status: str) -> list[Task]:
        """Find tasks by status."""
        pass


class ITeamRepository(IRepository[Team]):
    """Team repository interface."""

    @abstractmethod
    async def find_by_project(self, project_id: UUID) -> Optional[Team]:
        """Find team for a project."""
        pass


class ITeamMemberRepository(IRepository[TeamMember]):
    """Team member repository interface."""

    @abstractmethod
    async def find_by_team(self, team_id: UUID) -> list[TeamMember]:
        """Find all members of a team."""
        pass

    @abstractmethod
    async def find_by_user(self, user_id: UUID) -> list[TeamMember]:
        """Find all team memberships for a user."""
        pass


class IMilestoneRepository(IRepository[Milestone]):
    """Milestone repository interface."""

    @abstractmethod
    async def find_by_project(self, project_id: UUID) -> list[Milestone]:
        """Find all milestones for a project."""
        pass


class ICommentRepository(IRepository[Comment]):
    """Comment repository interface."""

    @abstractmethod
    async def find_by_entity(self, entity_type: str, entity_id: UUID) -> list[Comment]:
        """Find all comments for an entity."""
        pass


class IAttachmentRepository(IRepository[Attachment]):
    """Attachment repository interface."""

    @abstractmethod
    async def find_by_entity(self, entity_type: str, entity_id: UUID) -> list[Attachment]:
        """Find all attachments for an entity."""
        pass
