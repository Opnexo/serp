# serp-core

> Core foundation for the SimpleERP platform

[![PyPI version](https://badge.fury.io/py/serp-core.svg)](https://badge.fury.io/py/serp-core)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)

## Overview

`serp-core` provides the foundational building blocks for the SimpleERP platform, including:

- **Domain-Driven Design patterns**: Base classes for Entities, Value Objects, Aggregates, Repositories, and Domain Services
- **Application layer abstractions**: Service base classes, DTOs, and Unit of Work pattern
- **Plugin system**: Module discovery and registration via Python entry points
- **Authentication & Authorization**: Permission decorators, role management, and auth context
- **UI integration types**: Route and toolbar configuration for frontend integration
- **Configuration utilities**: Settings management and validation
- **Standard exceptions**: Domain, application, and auth exceptions

## Installation

```bash
# Using uv (recommended)
uv add serp-core

# Using pip
pip install serp-core
```

## Quick Start

### Domain Entity

```python
from serp_core.domain import Entity
from dataclasses import dataclass
from uuid import UUID

@dataclass
class Customer(Entity):
    name: str
    email: str
    
    def change_email(self, new_email: str) -> None:
        # Domain logic here
        self.email = new_email
```

### Value Object

```python
from serp_core.domain import ValueObject
from dataclasses import dataclass

@dataclass(frozen=True)
class Email(ValueObject):
    address: str
    
    def __post_init__(self):
        if '@' not in self.address:
            raise ValueError("Invalid email address")
```

### Repository Interface

```python
from serp_core.domain import Repository
from typing import Optional
from uuid import UUID

class CustomerRepository(Repository[Customer]):
    async def find_by_email(self, email: str) -> Optional[Customer]:
        raise NotImplementedError
```

### Application Service

```python
from serp_core.application import ApplicationService

class CustomerService(ApplicationService):
    def __init__(self, repository: CustomerRepository):
        self.repository = repository
    
    async def register_customer(self, name: str, email: str) -> Customer:
        customer = Customer(name=name, email=email)
        await self.repository.save(customer)
        return customer
```

### Permission Decorator

```python
from serp_core.auth import require_permission

@require_permission("customers.create")
async def create_customer_endpoint(data: dict):
    # This endpoint requires "customers.create" permission
    pass
```

## Module Information

Every SERP module must export a `MODULE_INFO` object:

```python
from serp_core.plugins import ModuleInfo

MODULE_INFO = ModuleInfo(
    name="serp-users",
    version="1.0.0",
    display_name="User Management",
    description="User authentication and management",
    author="SimpleERP Team",
    dependencies=["serp-core>=1.0.0"],
    entry_points={
        "api": "serp_users.Interfaces.API:load_api_routes",
        "ui": "serp_users.UI:registry",
    }
)
```

## Architecture

The package follows Domain-Driven Design principles:

```
serp_core/
├── domain/          # Pure domain logic (no dependencies)
├── application/     # Application services and DTOs
├── auth/           # Authentication and authorization
├── plugins/        # Module discovery and loading
├── ui/             # UI integration types
├── config/         # Configuration management
└── exceptions/     # Standard exceptions
```

## Development

```bash
# Clone the repository
git clone https://github.com/simpleerp/serp.git
cd serp/packages/serp-core

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=serp_core
```

## Documentation

- [Full Documentation](https://docs.simpleerp.dev)
- [API Reference](https://docs.simpleerp.dev/api/serp-core)
- [Architecture Guide](https://docs.simpleerp.dev/architecture)

## License

MIT License - see [LICENSE](../../LICENSE) for details
