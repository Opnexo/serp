# serp-shell

> FastAPI application shell and runtime for SimpleERP

## Overview

`serp-shell` provides the runtime environment for SERP applications:

- **FastAPI application**: REST API with automatic OpenAPI documentation
- **Module orchestration**: Loads and initializes all installed modules
- **Authentication**: JWT-based auth with session management
- **Middleware**: CORS, logging, error handling
- **Startup system**: Module discovery and initialization
- **CLI commands**: `serp run`, `serp dev` for running the application

## Installation

```bash
uv add serp-shell
```

## Quick Start

### Running the Server

```bash
# Development mode with auto-reload
serp dev

# Production mode
serp run
```

### Creating a Custom Application

```python
from serp_shell.api import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Configuration

Create a `config/settings.yaml` file:

```yaml
app:
  title: "My ERP System"
  debug: false
  cors_origins:
    - "http://localhost:3000"

database:
  url: "postgresql://user:pass@localhost/myerp"

auth:
  secret_key: "your-secret-key"
  algorithm: "HS256"
  access_token_expire_minutes: 30

modules:
  enabled:
    - serp-users
    - serp-crm
    - serp-invoicing
```

## API Routes

Once running, the API is available at:

- **Docs**: http://localhost:8000/docs
- **OpenAPI**: http://localhost:8000/openapi.json
- **Health**: http://localhost:8000/health

Module routes are automatically registered:
- `/api/users/*` (from serp-users)
- `/api/customers/*` (from serp-crm)
- etc.

## License

MIT License - see [LICENSE](../../LICENSE) for details
