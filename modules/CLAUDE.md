# CLAUDE.md - {{ cookiecutter.project_name }}

> Context file for AI-assisted development on this SERP module

---

## Module Overview

**{{ cookiecutter.project_name }}** (`{{ cookiecutter.module_slug }}`) is a SERP module that provides:
- {{ cookiecutter.description }}

**Package**: `{{ cookiecutter.project_slug }}` (PyPI)  
**Import**: `{{ cookiecutter.module_slug }}`

---

## Module Structure

```
{{ cookiecutter.module_slug }}/
├── __init__.py              # MODULE_INFO export
├── config.py                # Module settings (including database schema)
│
├── domain/                  # Core business logic (NO external dependencies)
│   ├── entities/            # Objects with unique identity
│   ├── value_objects/       # Immutable value types
│   ├── events/              # Domain events THIS MODULE PUBLISHES
│   ├── repositories.py      # Repository interfaces (ABC only)
│   └── services/            # Domain services
│
├── application/             # Use case orchestration
│   ├── services/            # Application services
│   ├── dtos/                # Data transfer objects
│   └── event_handlers/      # Handlers for OTHER modules' events
│
├── infrastructure/          # External integrations
│   ├── persistence/         # Database layer
│   │   ├── models.py        # SQLAlchemy models (with schema support)
│   │   ├── mappers.py       # Entity <-> Model mappers
│   │   ├── database.py      # DatabaseManager, session handling
│   │   ├── repositories/    # Repository implementations
│   │   │   ├── memory.py    # InMemory*Repository (testing)
│   │   │   └── postgres.py  # Postgres*Repository (production)
│   │   └── migrations/      # Alembic migrations
│   └── adapters/            # External service adapters
│
├── interfaces/              # Entry points
│   ├── api/                 # FastAPI routes
│   ├── controllers/         # Request handlers
│   └── permissions/         # Permission definitions
│
└── ui/                      # Frontend components
    ├── registry.ts          # Toolbar and route registration
    ├── permissions.ts       # Permission constants (must match backend)
    ├── views/               # Page components
    └── components/          # Module-specific components
```

---

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `MODULE_INFO` for plugin discovery |
| `config.py` | Module settings (database schema, feature flags) |
| `domain/repositories.py` | Repository interfaces (ABC) |
| `domain/events/*.py` | Events this module publishes |
| `infrastructure/persistence/models.py` | SQLAlchemy models with schema support |
| `infrastructure/persistence/repositories/memory.py` | In-memory repositories (testing) |
| `infrastructure/persistence/repositories/postgres.py` | PostgreSQL repositories (production) |
| `infrastructure/persistence/migrations/` | Alembic migrations |
| `application/event_handlers/__init__.py` | Registers handlers for other modules' events |
| `interfaces/api/__init__.py` | `load_api_routes()` entry point |
| `interfaces/permissions/*_permissions.py` | Permission constants |
| `ui/registry.ts` | Toolbar tabs, groups, buttons, routes |
| `ui/permissions.ts` | Frontend permission constants |

---

## Entry Points (pyproject.toml)

```toml
[project.entry-points."serp.modules"]
info = "{{ cookiecutter.module_slug }}:MODULE_INFO"
api = "{{ cookiecutter.module_slug }}.Interfaces.API:load_api_routes"
ui = "{{ cookiecutter.module_slug }}.UI:load_ui_config"

[project.entry-points."serp.event_handlers"]
{{ cookiecutter.module_slug }} = "{{ cookiecutter.module_slug }}.Application.EventHandlers:load_event_handlers"
```

---

## Permissions

### Backend Definition

```python
# Interfaces/Permissions/{{ cookiecutter.module_slug }}_permissions.py

class {{ cookiecutter.module_name }}Permissions:
    # List/Read
    LIST_READ = "{{ cookiecutter.module_slug }}.list.read"
    DETAIL_READ = "{{ cookiecutter.module_slug }}.detail.read"
    
    # Write
    ITEM_CREATE = "{{ cookiecutter.module_slug }}.item.create"
    ITEM_UPDATE = "{{ cookiecutter.module_slug }}.item.update"
    ITEM_DELETE = "{{ cookiecutter.module_slug }}.item.delete"
```

### Frontend Definition (MUST MATCH)

```typescript
// UI/permissions.ts

export const PERMISSIONS = {
  LIST_READ: "{{ cookiecutter.module_slug }}.list.read",
  DETAIL_READ: "{{ cookiecutter.module_slug }}.detail.read",
  ITEM_CREATE: "{{ cookiecutter.module_slug }}.item.create",
  ITEM_UPDATE: "{{ cookiecutter.module_slug }}.item.update",
  ITEM_DELETE: "{{ cookiecutter.module_slug }}.item.delete",
} as const;
```

---

## Domain Events

### Events This Module Publishes

Define in `Domain/Events/`:

```python
# Domain/Events/example_created.py

from dataclasses import dataclass
from uuid import UUID
from serp_core.events.domain.base_event import DomainEvent

@dataclass(frozen=True)
class ExampleCreatedEvent(DomainEvent):
    """
    Published when a new Example is created.
    
    Subscribers:
    - List modules that might subscribe
    """
    example_id: UUID
    # Include essential data, not entire objects
    
    @classmethod
    def event_type(cls) -> str:
        return "{{ cookiecutter.module_slug }}.example.created"
```

### Handling Events from Other Modules

Register in `Application/EventHandlers/__init__.py`:

```python
from serp_core.events.ports.event_bus import IEventBus

def load_event_handlers(event_bus: IEventBus) -> None:
    # Import events from other modules
    from serp_invoicing.Domain.Events import InvoiceCreatedEvent
    from .invoice_handlers import on_invoice_created
    
    event_bus.subscribe(InvoiceCreatedEvent, on_invoice_created)
```

---

## PostgreSQL Schema Per Module

Each module uses its own PostgreSQL schema for table isolation:

```python
# In config.py
from pydantic_settings import BaseSettings

class ModuleSettings(BaseSettings):
    """Module settings."""

    # Database configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/serp"
    database_schema: str = "module_name"  # e.g., "crm", "users", "invoicing"

    class Config:
        env_prefix = "SERP_MODULE_"  # e.g., SERP_CRM_DATABASE_SCHEMA
```

**Key Points:**
- Schema name = module name (e.g., `crm`, `users`, `invoicing`)
- All modules share the same database (`serp`)
- Configurable via environment variable: `SERP_{MODULE}_DATABASE_SCHEMA`
- Migrations must create schema: `CREATE SCHEMA IF NOT EXISTS {schema}`

### SQLAlchemy Models with Schema

```python
# In infrastructure/persistence/models.py
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from module.config import ModuleSettings

_settings = ModuleSettings()
MODULE_SCHEMA = _settings.database_schema

metadata = MetaData(schema=MODULE_SCHEMA)

class Base(DeclarativeBase):
    metadata = metadata

class EntityModel(Base):
    __tablename__ = "entities"  # Will be created in MODULE_SCHEMA
    # Foreign keys must include schema: f"{MODULE_SCHEMA}.other_table.id"
```

---

## Repository Structure

Repositories are organized inside `infrastructure/persistence/repositories/`:

```python
# persistence/repositories/__init__.py

# In-memory (for testing)
from .memory import InMemoryEntityRepository

# PostgreSQL (for production)
from .postgres import PostgresEntityRepository

# Backward compatibility alias
SQLAlchemyEntityRepository = PostgresEntityRepository
```

### Usage

```python
# In-memory (for testing)
from module.infrastructure import InMemoryEntityRepository

# PostgreSQL (for production)
from module.infrastructure import PostgresEntityRepository

# With session dependency injection
repo = PostgresEntityRepository(session)
entity = await repo.get_by_id("123")
```

---

## Common Tasks

### Adding a New Entity

1. Create entity in `domain/entities/`
2. Create repository interface in `domain/repositories.py`
3. Create SQLAlchemy model in `infrastructure/persistence/models.py`
4. Create mapper in `infrastructure/persistence/mappers.py`
5. Create repository implementations:
   - `infrastructure/persistence/repositories/memory.py` (testing)
   - `infrastructure/persistence/repositories/postgres.py` (production)
6. Create DTOs in `application/dtos/`
7. Create service in `application/services/`
8. Create API routes in `interfaces/api/`
9. Add permissions to `interfaces/permissions/`
10. Add UI view in `ui/views/`
11. Register in toolbar in `ui/registry.ts`

### Adding a New Permission

1. Add to backend: `Interfaces/Permissions/{{ cookiecutter.module_slug }}_permissions.py`
2. Add to frontend: `UI/permissions.ts`
3. Use in API: `@require_permission("{{ cookiecutter.module_slug }}.new.permission")`
4. Use in UI registry: `permission: PERMISSIONS.NEW_PERMISSION`

### Publishing an Event

```python
# In Application Service
async def create_example(self, request: CreateExampleRequest) -> ExampleDTO:
    example = Example(...)
    await self._repository.save(example)
    
    await self._event_bus.publish(
        ExampleCreatedEvent(example_id=example.id)
    )
    
    return ExampleDTO.from_entity(example)
```

---

## Testing

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov={{ cookiecutter.module_slug }}

# Specific file
uv run pytest tests/test_domain/test_example.py
```

### Test Structure

```
tests/
├── test_domain/           # Domain layer tests (most important)
│   ├── test_entities.py
│   └── test_value_objects.py
├── test_application/      # Application service tests
│   └── test_services.py
└── test_api/              # API endpoint tests
    └── test_routes.py
```

### Testing Event Handlers

```python
@pytest.mark.asyncio
async def test_handles_invoice_created():
    event_bus = InMemoryEventBus()
    load_event_handlers(event_bus)
    
    event = InvoiceCreatedEvent(invoice_id=uuid4(), ...)
    await event_bus.publish(event)
    
    # Assert side effects
```

---

## Anti-Patterns

### ❌ Don't Import Other Modules' Internal Code

```python
# ❌ WRONG
from serp_invoicing.Application.Services import InvoiceService
from serp_invoicing.Infrastructure.Repositories import InvoiceRepo

# ✅ CORRECT - Only import events (public contract)
from serp_invoicing.Domain.Events import InvoiceCreatedEvent
```

### ❌ Don't Put Business Logic in Infrastructure

```python
# ❌ WRONG - Logic in repository
class ExampleRepository:
    async def save(self, example):
        if example.status == "invalid":  # Business rule!
            raise ValueError()

# ✅ CORRECT - Logic in domain
class Example(Entity):
    def validate(self):
        if self.status == "invalid":
            raise DomainException()
```

### ❌ Don't Forget Permission Sync

```python
# Backend has permission but frontend doesn't = broken UI
# Frontend has permission but backend doesn't = security hole

# ALWAYS keep these in sync:
# - Interfaces/Permissions/{{ cookiecutter.module_slug }}_permissions.py
# - UI/permissions.ts
```

---

## Development Commands

```bash
# Install in development mode
uv pip install -e .

# Run linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy {{ cookiecutter.module_slug }}/

# Build package
uv build

# Publish to PyPI
uv publish
```

---

## Questions Before Changes

1. **Which layer does this belong to?** Domain, Application, Infrastructure, or Interface?
2. **Should this publish an event?** Will other modules care about this action?
3. **Does this need a new permission?** Any new action needs authorization.
4. **Is the permission synced?** Backend and frontend must match.
5. **Are there tests?** Especially for domain logic.

---

*Generated from serp-module-template*
