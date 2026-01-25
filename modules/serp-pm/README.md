# SERP Project Management Core Module

Foundational project management module for the SERP platform. Designed to be extended by methodology-specific modules (Scrum, Kanban, CMMI, etc.).

## Features

### Core Functionality
- **Project Management**: Create, update, and organize projects
- **Task Management**: Generic task/work item tracking
- **Team Management**: Team composition and member assignments
- **Milestones**: Project milestone tracking
- **Comments & Collaboration**: Discussion threads on projects/tasks
- **Attachments**: Link files to projects and tasks

### Extensibility
This module provides a **foundation** for methodology-specific extensions:
- `serp-pm-scrum` → Adds Sprints, Backlogs, User Stories, Planning Poker
- `serp-pm-kanban` → Adds Boards, Columns, Cards, WIP limits, Flow metrics
- `serp-pm-cmm` → Adds CMMI Process Areas, Goals, Practices, Maturity Levels

Extension modules use the existing SERP plugin system and subscribe to core PM events.

## Installation

```bash
uv add serp-pm
```

## Quick Start

### 1. Basic Usage

```python
from serp_pm.application.services import ProjectService, TaskService
from serp_pm.infrastructure.persistence.repositories import PostgresProjectRepository

# Create services
project_repo = PostgresProjectRepository(db_session)
project_service = ProjectService(project_repo)

# Create a project
project = await project_service.create_project(
    name="Website Redesign",
    description="Complete website overhaul",
    start_date=date(2026, 2, 1),
    end_date=date(2026, 6, 30),
)

# Create tasks
task = await task_service.create_task(
    project_id=project.id,
    title="Design homepage mockup",
    description="Create wireframes and high-fidelity designs",
    priority="HIGH",
)
```

### 2. Extending with Methodology Modules

Install methodology extensions as needed:

```bash
# For Scrum
uv add serp-pm-scrum

# For Kanban
uv add serp-pm-kanban
```

## API Endpoints

All endpoints are registered at `/api/pm/*`:

### Projects
- `GET /api/pm/projects` - List projects (paginated)
- `GET /api/pm/projects/{id}` - Get project details
- `POST /api/pm/projects` - Create project
- `PUT /api/pm/projects/{id}` - Update project
- `DELETE /api/pm/projects/{id}` - Delete project

### Tasks
- `GET /api/pm/tasks` - List tasks (paginated, filterable)
- `GET /api/pm/tasks/{id}` - Get task details
- `POST /api/pm/tasks` - Create task
- `PUT /api/pm/tasks/{id}` - Update task
- `DELETE /api/pm/tasks/{id}` - Delete task
- `PUT /api/pm/tasks/{id}/assign` - Assign task to user

### Teams
- `GET /api/pm/teams` - List teams
- `POST /api/pm/teams` - Create team
- `POST /api/pm/teams/{id}/members` - Add team member

## Permissions

Module permissions follow the pattern `pm:<resource>:<action>`:

### Project Permissions
- `pm.project.list` - List projects
- `pm.project.read` - Read project details
- `pm.project.create` - Create projects
- `pm.project.update` - Update projects
- `pm.project.delete` - Delete projects

### Task Permissions
- `pm.task.list` - List tasks
- `pm.task.read` - Read task details
- `pm.task.create` - Create tasks
- `pm.task.update` - Update tasks
- `pm.task.delete` - Delete tasks
- `pm.task.assign` - Assign tasks to users

### Team Permissions
- `pm.team.list` - List teams
- `pm.team.read` - Read team details
- `pm.team.create` - Create teams
- `pm.team.manage_members` - Add/remove team members

## Domain Model

### Core Entities

#### Project (Aggregate Root)
```python
@dataclass
class Project(AggregateRoot):
    name: str
    description: str
    start_date: Optional[date]
    end_date: Optional[date]
    status: str  # PLANNING, ACTIVE, ON_HOLD, COMPLETED, CANCELLED
    owner_id: UUID
    team_id: Optional[UUID]
```

#### Task
```python
@dataclass
class Task(Entity):
    project_id: UUID
    title: str
    description: str
    status: str  # OPEN, IN_PROGRESS, DONE, CLOSED
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL
    assigned_to: Optional[UUID]
    estimate: Optional[TimeEstimate]
    parent_id: Optional[UUID]  # For subtasks
```

#### Team
```python
@dataclass
class Team(Entity):
    name: str
    description: str
    project_id: Optional[UUID]
```

## Extension Architecture

Methodology modules extend serp-pm by:

1. **Depending on serp-pm** in `pyproject.toml`
2. **Adding their own entities** that reference core PM entities
3. **Subscribing to core events** (ProjectCreated, TaskStatusChanged, etc.)
4. **Using SERP plugin discovery** (no new plugin system needed)

See [Extension Guide](docs/extending.md) for details.

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy serp_pm

# Linting
uv run ruff check serp_pm
```

## License

MIT License - See LICENSE file for details
