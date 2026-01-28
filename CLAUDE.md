# CLAUDE.md - SERP (SimpleERP) Main Repository

> Context file for AI-assisted development on the SERP ecosystem

---

## Project Overview

SERP (SimpleERP) is a **modular, plugin-based ERP platform** built with:
- **Backend**: Python 3.11+, FastAPI, Domain-Driven Design
- **Frontend**: NextJS 14+, TypeScript, Tailwind CSS
- **Architecture**: Distributed modules as PyPI packages

This is the **main monorepo** containing core packages and official modules.

---

## Repository Structure

```
serp/
├── packages/                 # Core PyPI packages
│   ├── serp-core/           # Base classes, auth, events, plugins
│   ├── serp-shell/          # FastAPI app, NextJS shell, worker
│   └── serp-cli/            # Developer CLI tools
│
├── modules/                  # Official SERP modules
│   ├── serp-users/          # User management, auth, RBAC
│   ├── serp-crm/            # Customer relationship management
│   ├── serp-invoicing/      # Invoice management
│   └── ...
│
├── ui-shell/                 # NextJS frontend application
│
├── docs/                     # Documentation (markdown)
│
└── scripts/                  # Build, release, dev scripts
```

---

## Key Architectural Principles

### 1. Modules are Self-Contained PyPI Packages

Each module is an independent package with:
- Its own `pyproject.toml`
- Entry points for discovery (`serp.modules`, `serp.event_handlers`)
- Domain, Application, Infrastructure, Interface, and UI layers

### 2. Events Belong to Modules, Not Core

```python
# ✅ CORRECT: Event in its owning module
# serp_invoicing/Domain/Events/invoice_created.py
class InvoiceCreatedEvent(DomainEvent):
    invoice_id: UUID
    ...

# ❌ WRONG: Events in serp-core
# serp_core/events/invoice_created.py  # DON'T DO THIS
```

### 3. Technology-Agnostic Interfaces

Modules depend on interfaces, not implementations:
```python
# Module uses IEventBus, not RedisEventBus
def __init__(self, event_bus: IEventBus):  # ✅
def __init__(self, event_bus: RedisEventBus):  # ❌
```

### 4. Plugin Discovery via Entry Points

```toml
# In module's pyproject.toml
[project.entry-points."serp.modules"]
info = "serp_invoicing:MODULE_INFO"
api = "serp_invoicing.Interfaces.API:load_api_routes"
ui = "serp_invoicing.UI:load_ui_config"

[project.entry-points."serp.event_handlers"]
invoicing = "serp_invoicing.Application.EventHandlers:load_event_handlers"
```

### 5. Permission-Based UI Rendering

- Backend expands roles → flat permission list (SET UNION for multiple roles)
- Frontend receives explicit permissions only (no wildcards)
- UI components filtered at runtime based on permissions
- Code for unauthorized views never reaches client

### 6. PostgreSQL Schema Per Module

Each module uses its own PostgreSQL schema for table isolation:

```python
# In module's config.py
class ModuleSettings(BaseSettings):
    database_schema: str = "module_name"  # e.g., "crm", "invoicing"

    class Config:
        env_prefix = "SERP_MODULE_"  # e.g., SERP_CRM_DATABASE_SCHEMA
```

**Benefits:**
- Table isolation between modules (no name collisions)
- Clean database organization
- Easier backups per module
- Independent migrations per module

**Convention:**
- Schema name = module name (e.g., `crm`, `users`, `invoicing`)
- All modules share the same database (`serp`)
- Configurable via environment variable: `SERP_{MODULE}_DATABASE_SCHEMA`

### 7. Repository Structure

Repositories are organized inside `infrastructure/persistence/repositories/`:

```python
# In-memory (for testing)
from serp_crm.infrastructure import InMemoryPartnerRepository

# PostgreSQL (for production)
from serp_crm.infrastructure import PostgresPartnerRepository

# Backward compatibility alias
from serp_crm.infrastructure import SQLAlchemyPartnerRepository  # = PostgresPartnerRepository
```

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Package names | `serp-{name}` (PyPI) | `serp-invoicing` |
| Module imports | `serp_{name}` (Python) | `serp_invoicing` |
| Entry point groups | `serp.{type}` | `serp.modules`, `serp.event_handlers` |
| Permissions | `{module}.{resource}.{action}` | `invoicing.invoice.create` |
| Events | PastTense + Event | `InvoiceCreatedEvent` |
| Event types | `{module}.{aggregate}.{action}` | `invoicing.invoice.created` |

---

## Module Structure (DDD Layers)

```
serp_{module}/
├── __init__.py              # MODULE_INFO export
├── config.py                # Module settings (including database schema)
├── domain/
│   ├── entities/            # Business objects with identity
│   ├── value_objects/       # Immutable value types
│   ├── events/              # Domain events (THIS MODULE OWNS)
│   ├── repositories.py      # Repository interfaces (ABC)
│   └── services/            # Domain services
├── application/
│   ├── services/            # Use case orchestration
│   ├── dtos/                # Data transfer objects
│   └── event_handlers/      # Handlers for OTHER modules' events
├── infrastructure/
│   ├── persistence/         # Database layer
│   │   ├── models.py        # SQLAlchemy models (with schema support)
│   │   ├── mappers.py       # Entity <-> Model mappers
│   │   ├── database.py      # DatabaseManager, session handling
│   │   ├── repositories/    # Repository implementations
│   │   │   ├── memory.py    # InMemory*Repository (testing)
│   │   │   └── postgres.py  # Postgres*Repository (production)
│   │   └── migrations/      # Alembic migrations
│   └── adapters/            # External service adapters
├── interfaces/
│   ├── api/                 # FastAPI routes
│   ├── controllers/         # Request handlers
│   └── permissions/         # Permission definitions
└── ui/
    ├── registry.ts          # Toolbar and route config
    ├── permissions.ts       # Frontend permission constants
    ├── views/               # Page components
    └── components/          # Module-specific components
```

---

## Common Tasks

### Adding a New Official Module

```bash
cd modules/
cookiecutter gh:simpleserp/serp-module-template
# Fill in: serp-{name}, description, etc.

# Install in development mode
cd serp-{name}
uv pip install -e .
```

### Running the Development Server

```bash
# API only
cd packages/serp-shell
uvicorn serp_shell.api:app --reload

# With UI
cd ui-shell
npm run dev

# Event worker
python -m serp_shell.worker
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific package
uv run pytest packages/serp-core/

# With coverage
uv run pytest --cov=serp_core packages/serp-core/
```

---

## Anti-Patterns to Avoid

### ❌ Don't Import Between Modules (except Events)

```python
# ❌ WRONG: Direct import of another module's service
from serp_invoicing.Application.Services import InvoiceService

# ✅ CORRECT: Import only the event (public contract)
from serp_invoicing.Domain.Events import InvoiceCreatedEvent
```

### ❌ Don't Put Business Logic in Infrastructure

```python
# ❌ WRONG: Business logic in repository
class InvoiceRepository:
    def save(self, invoice):
        if invoice.total < 0:  # Business rule in infra!
            raise ValueError("Invalid total")

# ✅ CORRECT: Business logic in domain
class Invoice(Entity):
    def __post_init__(self):
        if self.total < Money.zero():
            raise DomainException("Invalid total")
```

### ❌ Don't Hardcode Module Lists

```python
# ❌ WRONG: Hardcoded module list
MODULES = ["serp_users", "serp_invoicing", "serp_crm"]

# ✅ CORRECT: Discovery via entry points
from importlib.metadata import entry_points
modules = entry_points(group="serp.modules")
```

### ❌ Don't Store Permissions in Frontend

```typescript
// ❌ WRONG: Permissions in localStorage
localStorage.setItem("permissions", JSON.stringify(perms));

// ✅ CORRECT: Permissions in memory only (React Context)
const { permissions } = usePermissions();
```

---

## Key Files to Understand

| File | Purpose |
|------|---------|
| `packages/serp-core/serp_core/events/ports/event_bus.py` | IEventBus interface |
| `packages/serp-core/serp_core/auth/permissions.py` | Permission and PermissionSet classes |
| `packages/serp-core/serp_core/plugins/discovery.py` | Entry point discovery logic |
| `packages/serp-shell/serp_shell/api/app.py` | FastAPI application factory |
| `packages/serp-shell/serp_shell/worker/main.py` | Event consumer worker |
| `ui-shell/src/lib/permissions/PermissionContext.tsx` | Frontend permission state |
| `ui-shell/src/components/Ribbon/Ribbon.tsx` | Office-style toolbar |

---

## Documentation References

For detailed specifications, see `/docs/`:
- `00-ECOSYSTEM-OVERVIEW.md` - Start here
- `architecture/02-PLUGIN-SYSTEM.md` - Entry points and discovery
- `architecture/03-PERMISSION-SYSTEM.md` - Authorization
- `architecture/05-EVENT-DRIVEN-ARCHITECTURE.md` - Inter-module events
- `specifications/01-SERP-CORE-SPEC.md` - Core package details

---

## Environment Setup

```bash
# Prerequisites
python --version  # 3.11+
node --version    # 20+
uv --version      # Latest

# Clone and setup
git clone https://github.com/simpleserp/serp.git
cd serp
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

---

User Interface

- Use shadcn/ui for consistent design
- Follow component structure in `ui/` folders of each module

---

## Questions to Ask Before Making Changes

1. **Which package/module does this belong to?**
2. **Does this change affect the public API (breaking change)?**
3. **Should this be in Domain, Application, or Infrastructure layer?**
4. **Does this module need to publish an event for others to react?**
5. **Are there permission implications for the UI?**
6. **Is this a cross-cutting concern that belongs in serp-core?**

---

*Last updated: December 2025*
