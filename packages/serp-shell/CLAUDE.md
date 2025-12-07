# CLAUDE.md - serp-shell Package

> Context file for AI-assisted development on serp-shell

---

## Package Purpose

`serp-shell` is the **runtime container** for SERP. It provides:
- FastAPI application with automatic module route loading
- NextJS UI shell with Office-style Ribbon toolbar
- Event consumer worker process
- Module discovery and registration

**This package orchestrates modules but contains NO business logic.**

---

## Package Structure

```
serp_shell/
├── __init__.py
│
├── api/                     # FastAPI Backend
│   ├── app.py               # Application factory
│   ├── middleware/          # Auth, CORS, logging
│   ├── routes/              # Core routes (health, auth)
│   └── dependencies.py      # Dependency injection
│
├── worker/                  # Event Consumer
│   ├── main.py              # Worker entry point
│   ├── config.py            # Worker configuration
│   └── discovery.py         # Handler auto-discovery
│
├── plugins/                 # Module Loading
│   ├── loader.py            # Load modules from entry points
│   ├── router.py            # Aggregate API routes
│   └── events.py            # Aggregate event handlers
│
├── auth/                    # Authentication
│   ├── jwt.py               # JWT token handling
│   ├── middleware.py        # Auth middleware
│   └── endpoints.py         # Login, logout, refresh
│
└── config/                  # Configuration
    ├── settings.py          # Pydantic settings
    └── logging.py           # Logging configuration
```

### UI Shell (ui-shell/)

```
ui-shell/
├── src/
│   ├── app/                 # NextJS App Router
│   │   ├── layout.tsx       # Root layout
│   │   ├── (auth)/          # Auth routes (login, logout)
│   │   └── (protected)/     # Protected routes with shell
│   │       ├── layout.tsx   # Shell layout with Ribbon
│   │       └── [...slug]/   # Dynamic module routes
│   │
│   ├── components/
│   │   ├── Shell/           # Main shell wrapper
│   │   ├── Ribbon/          # Office-style toolbar
│   │   └── ModuleLoader/    # Dynamic component loading
│   │
│   └── lib/
│       ├── auth/            # Auth context, hooks
│       ├── permissions/     # Permission context, hooks
│       └── modules/         # Module registry, loader
```

---

## Key Responsibilities

### 1. Module Discovery

```python
# serp_shell/plugins/loader.py

def discover_modules() -> List[LoadedModule]:
    """
    Discover all installed SERP modules via entry points.
    
    Looks for: serp.modules group
    """
    from importlib.metadata import entry_points
    
    modules = []
    for ep in entry_points(group="serp.modules"):
        info_func = ep.load()
        module_info = info_func()
        modules.append(LoadedModule(info=module_info, entry_point=ep))
    
    return modules
```

### 2. API Route Aggregation

```python
# serp_shell/api/app.py

def create_app() -> FastAPI:
    app = FastAPI(title="SERP API")
    
    # Core routes
    app.include_router(auth_router, prefix="/api/auth")
    app.include_router(health_router, prefix="/api")
    
    # Module routes (auto-discovered)
    for module in discover_modules():
        if module.api_loader:
            router = module.api_loader()
            app.include_router(router, prefix=f"/api/{module.slug}")
    
    return app
```

### 3. Event Handler Discovery

```python
# serp_shell/worker/discovery.py

def discover_and_register_handlers(event_bus: IEventBus) -> int:
    """
    Discover and register event handlers from all modules.
    
    Looks for: serp.event_handlers group
    """
    from importlib.metadata import entry_points
    
    count = 0
    for ep in entry_points(group="serp.event_handlers"):
        load_handlers = ep.load()
        load_handlers(event_bus)
        count += 1
    
    return count
```

### 4. Permission-Based UI Filtering

```typescript
// ui-shell/src/lib/permissions/filter.ts

export function filterByPermissions(
  toolbar: ToolbarTab,
  permissions: Set<string>
): ToolbarTab {
  // Remove buttons user doesn't have permission for
  const filteredGroups = toolbar.groups
    .map(group => ({
      ...group,
      buttons: group.buttons.filter(btn => 
        permissions.has(btn.permission)
      ),
    }))
    .filter(group => group.buttons.length > 0);

  return { ...toolbar, groups: filteredGroups };
}
```

---

## Authentication Flow

```
┌────────────┐     POST /api/auth/login     ┌────────────┐
│   Client   │ ────────────────────────────► │   Shell    │
│            │                               │   API      │
│            │ ◄──────────────────────────── │            │
└────────────┘   { token, permissions[] }   └────────────┘
                                                   │
                 Permissions are FLAT list         │
                 (roles already expanded)          │
                                                   ▼
                                            ┌────────────┐
                                            │  Database  │
                                            │  (Users,   │
                                            │   Roles)   │
                                            └────────────┘
```

### Login Response

```json
{
  "token": "eyJhbG...",
  "refreshToken": "dGhpc...",
  "expiresIn": 1800,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "roles": ["manager", "accountant"]
  },
  "permissions": [
    "invoicing.list.read",
    "invoicing.item.create",
    "payments.list.read"
  ]
}
```

---

## Event Worker

### Starting the Worker

```bash
# Development
python -m serp_shell.worker

# Production (with multiple instances)
gunicorn serp_shell.worker:main --workers 4
```

### Worker Output

```
🚀 Starting Event Worker: serp-worker-1
   Event Bus: redis
   Consumer Group: serp-workers

🔍 Discovering event handlers...
  ✓ serp-payments: Registered 3 handlers
  ✓ serp-invoicing: Registered 2 handlers
✅ Loaded handlers from 2 module(s)

📡 Event consumer started. Streams:
   - invoicing-events
   - payments-events
```

---

## Configuration

### Environment Variables

```bash
# API
SERP_ENV=production
SERP_DEBUG=false
SERP_SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/serp

# Events
EVENT_BUS_TYPE=redis  # or: memory, kafka
REDIS_URL=redis://localhost:6379
CONSUMER_GROUP=serp-workers

# JWT
JWT_SECRET_KEY=jwt-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Settings Class

```python
# serp_shell/config/settings.py

class Settings(BaseSettings):
    env: str = "development"
    debug: bool = False
    secret_key: str
    
    database_url: str
    
    event_bus_type: str = "redis"
    redis_url: str = "redis://localhost:6379"
    consumer_group: str = "serp-workers"
    
    jwt_secret_key: str
    jwt_access_token_expire_minutes: int = 30
    
    class Config:
        env_prefix = "SERP_"
```

---

## Common Tasks

### Adding a Core API Route

```python
# serp_shell/api/routes/system.py

from fastapi import APIRouter

router = APIRouter(tags=["System"])

@router.get("/modules")
async def list_modules():
    """List all loaded modules."""
    modules = discover_modules()
    return [{"id": m.id, "name": m.name, "version": m.version} for m in modules]
```

### Adding Middleware

```python
# serp_shell/api/middleware/timing.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        return response
```

### Modifying the UI Shell

```tsx
// ui-shell/src/components/Ribbon/Ribbon.tsx

// The Ribbon auto-loads tabs from discovered modules
// Only modify for shell-level changes, not module-specific
```

---

## Anti-Patterns

### ❌ Don't Add Business Logic

```python
# ❌ WRONG - Business logic in shell
@router.post("/invoices")
async def create_invoice(...):
    if invoice.total < 0:  # Business rule!
        raise HTTPException(...)

# ✅ CORRECT - Shell only routes to modules
# Invoice creation is in serp-invoicing module
```

### ❌ Don't Hardcode Module Lists

```python
# ❌ WRONG
MODULES = ["serp_users", "serp_invoicing"]

# ✅ CORRECT
modules = entry_points(group="serp.modules")
```

### ❌ Don't Store Secrets in Code

```python
# ❌ WRONG
JWT_SECRET = "hardcoded-secret"

# ✅ CORRECT
settings.jwt_secret_key  # From environment
```

---

## Deployment

### API + Worker (Separate)

```yaml
# docker-compose.yml
services:
  api:
    command: uvicorn serp_shell.api:app --host 0.0.0.0
    environment:
      - EVENT_CONSUMER_MODE=disabled
  
  worker:
    command: python -m serp_shell.worker
    environment:
      - CONSUMER_GROUP=serp-workers
```

### API + Worker (Embedded - Dev Only)

```python
# For development, worker can run in same process
app = create_app(embed_worker=True)
```

---

## Questions Before Changes

1. **Is this shell responsibility?** Or should it be in a module?
2. **Does this affect all modules?** Changes to shell affect everyone.
3. **Is this a breaking API change?** Modules depend on shell.
4. **Is security handled?** Auth middleware, permission checks.
5. **Is configuration externalized?** Use settings, not hardcoded values.

---

*Last updated: December 2025*
