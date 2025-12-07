# CLAUDE.md - serp-core Package

> Context file for AI-assisted development on serp-core

---

## Package Purpose

`serp-core` is the **foundation package** for the SERP ecosystem. It provides:
- Base classes for DDD (Entity, ValueObject, Repository, Service)
- Authentication and authorization primitives
- Event-driven architecture abstractions
- Plugin discovery system
- UI configuration types

**This package has NO business logic** - it's pure infrastructure for modules.

---

## Package Structure

```
serp_core/
├── domain/              # DDD base classes
│   ├── entity.py        # Entity, SoftDeletableEntity
│   ├── value_object.py  # ValueObject base
│   ├── aggregate.py     # AggregateRoot
│   ├── repository.py    # IRepository interface
│   └── service.py       # DomainService base
│
├── application/         # Application layer bases
│   ├── service.py       # ApplicationService base
│   ├── dto.py           # DTO, PaginatedResponse
│   └── unit_of_work.py  # IUnitOfWork interface
│
├── auth/                # Authorization system
│   ├── permissions.py   # Permission, PermissionSet
│   ├── decorators.py    # @require_permission
│   ├── context.py       # get_current_user()
│   └── user.py          # AuthenticatedUser type
│
├── events/              # Event-driven architecture
│   ├── domain/          # Event abstractions
│   │   ├── base_event.py      # DomainEvent base
│   │   └── event_metadata.py  # EventMetadata
│   ├── ports/           # Interfaces
│   │   ├── event_bus.py       # IEventBus
│   │   ├── event_publisher.py # IEventPublisher
│   │   └── event_subscriber.py
│   └── adapters/        # Implementations
│       ├── redis_event_bus.py
│       ├── kafka_event_bus.py
│       └── memory_event_bus.py
│
├── plugins/             # Plugin discovery
│   ├── types.py         # ModuleInfo, LoadedModule
│   ├── discovery.py     # Entry point discovery
│   └── registry.py      # ModuleRegistry
│
├── ui/                  # UI configuration types
│   ├── toolbar.py       # ToolbarButton, ToolbarGroup, ToolbarTab
│   └── routes.py        # RouteConfig, UIConfig
│
└── exceptions/          # Standard exceptions
    ├── domain.py        # DomainException, EntityNotFound
    ├── application.py   # ApplicationException
    ├── auth.py          # AuthException, PermissionDenied
    └── events.py        # EventException
```

---

## Key Design Decisions

### 1. Minimal Dependencies

```toml
# serp-core has very few dependencies
dependencies = [
    "pydantic>=2.0",
    "fastapi>=0.100",  # Only for auth context
]

# Redis/Kafka are optional
[project.optional-dependencies]
redis = ["redis>=5.0"]
kafka = ["aiokafka>=0.8"]
```

### 2. Abstract Base Classes Everywhere

```python
# Everything is an interface - implementations are in adapters or modules
class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]: ...

class IEventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None: ...
```

### 3. No Business Logic

```python
# ❌ WRONG: Business logic in serp-core
class Invoice(Entity):  # This belongs in serp-invoicing!
    pass

# ✅ CORRECT: Only abstract base
class Entity(ABC):
    id: UUID
```

---

## Common Patterns

### Creating a New Base Class

```python
# serp_core/domain/my_base.py

from abc import ABC
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")

@dataclass
class MyBase(ABC):
    """
    Base class for X.
    
    Usage in modules:
        from serp_core.domain.my_base import MyBase
        
        class ConcreteX(MyBase):
            ...
    """
    pass
```

### Adding a New Exception

```python
# serp_core/exceptions/domain.py

class DomainException(Exception):
    """Base exception for domain errors."""
    pass

class EntityNotFoundException(DomainException):
    """Raised when an entity is not found."""
    def __init__(self, entity_type: str, entity_id: UUID):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} not found: {entity_id}")
```

### Exporting from Package

```python
# serp_core/__init__.py

from .domain.entity import Entity, SoftDeletableEntity
from .domain.value_object import ValueObject
from .domain.repository import IRepository
from .auth.permissions import Permission, PermissionSet
from .auth.decorators import require_permission
from .events.domain.base_event import DomainEvent
from .events.ports.event_bus import IEventBus

__all__ = [
    "Entity",
    "SoftDeletableEntity",
    "ValueObject",
    "IRepository",
    "Permission",
    "PermissionSet",
    "require_permission",
    "DomainEvent",
    "IEventBus",
]
```

---

## Testing Guidelines

### Unit Tests for Base Classes

```python
# tests/domain/test_entity.py

def test_entity_equality_by_id():
    """Entities are equal if they have the same ID."""
    id = uuid4()
    e1 = ConcreteEntity(id=id, name="A")
    e2 = ConcreteEntity(id=id, name="B")
    assert e1 == e2  # Same ID = same entity

def test_value_object_equality_by_attributes():
    """Value objects are equal if all attributes match."""
    vo1 = Money(amount=Decimal("100"), currency="USD")
    vo2 = Money(amount=Decimal("100"), currency="USD")
    assert vo1 == vo2
```

### Testing Event Bus Adapters

```python
# tests/events/adapters/test_memory_event_bus.py

@pytest.mark.asyncio
async def test_publish_and_subscribe():
    bus = InMemoryEventBus()
    received = []
    
    bus.subscribe(TestEvent, lambda e: received.append(e))
    await bus.publish(TestEvent(data="test"))
    
    assert len(received) == 1
    assert received[0].data == "test"
```

---

## Anti-Patterns

### ❌ Don't Add Module-Specific Code

```python
# ❌ WRONG: Invoice-specific code in serp-core
# serp_core/domain/invoice.py
class Invoice(Entity):
    customer_id: UUID
    total: Decimal
```

### ❌ Don't Create Concrete Implementations Without Interface

```python
# ❌ WRONG: Concrete class without ABC
class EmailService:
    def send(self, to: str, body: str): ...

# ✅ CORRECT: Interface + Implementation
class IEmailService(ABC):
    @abstractmethod
    def send(self, to: str, body: str): ...

class SmtpEmailService(IEmailService):
    def send(self, to: str, body: str): ...
```

### ❌ Don't Import from Modules

```python
# ❌ WRONG: serp-core importing from a module
from serp_invoicing.Domain.Entities import Invoice

# serp-core should NEVER import from any serp-* module
```

---

## Key Interfaces to Know

### IRepository

```python
class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]: ...
    
    @abstractmethod
    async def save(self, entity: T) -> None: ...
    
    @abstractmethod
    async def delete(self, id: UUID) -> None: ...
```

### IEventBus

```python
class IEventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None: ...
    
    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None: ...
    
    @abstractmethod
    async def start(self) -> None: ...
    
    @abstractmethod
    async def stop(self) -> None: ...
```

### Permission Decorator

```python
@require_permission("invoicing.invoice.create")
async def create_invoice(request: CreateInvoiceRequest):
    ...
```

---

## Version Compatibility

- Python: 3.11+
- Pydantic: 2.x
- FastAPI: 0.100+

When updating dependencies, ensure backward compatibility with existing modules.

---

## Questions Before Changes

1. **Is this truly generic?** Would ALL modules potentially use this?
2. **Is this an interface or implementation?** Implementations go in adapters.
3. **Does this have external dependencies?** Keep core minimal.
4. **Is this a breaking change?** Consider deprecation path.
5. **Are there tests?** Core needs high test coverage.

---

*Last updated: December 2025*
