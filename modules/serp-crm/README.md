# SERP CRM Module

Customer Relationship Management module for the SERP platform using the Partner pattern.

## Features

- **Partner Management**: Unified entity for customers, suppliers, and other business partners
- **Contact Management**: People associated with partners
- **Lead Management**: Potential partners with qualification workflow
- **Opportunity Tracking**: Sales pipeline and deal management
- **Activity Logging**: Interactions, notes, calls, emails
- **Multi-Role Support**: Partners can be customers, suppliers, or both

## Partner Pattern

The Partner pattern provides a unified entity that can represent:
- **Customers** - People/companies who buy from you
- **Suppliers** - People/companies you buy from
- **Both** - Common in B2B (they sell to you AND buy from you)
- **Employees** - Can also be customers/suppliers
- **Other** - Distributors, agents, etc.

## Installation

```bash
uv add serp-crm
```

## Quick Start

```python
from serp_crm.application.services import PartnerService, ContactService
from serp_crm.infrastructure.repositories import InMemoryPartnerRepository

# Create services
partner_repo = InMemoryPartnerRepository()
partner_service = PartnerService(partner_repo)

# Create a partner (customer)
partner = await partner_service.create_partner(
    name="Acme Corp",
    partner_type="COMPANY",
    is_customer=True,
    email="contact@acme.com"
)

# Create a contact for the partner
contact = await contact_service.create_contact(
    partner_id=partner.id,
    first_name="John",
    last_name="Doe",
    email="john@acme.com",
    is_primary=True
)
```

## API Endpoints

All endpoints are registered at `/api/crm/*`:

### Partners
- `GET /api/crm/partners` - List partners
- `GET /api/crm/partners/{id}` - Get partner
- `POST /api/crm/partners` - Create partner
- `PUT /api/crm/partners/{id}` - Update partner
- `DELETE /api/crm/partners/{id}` - Delete partner
- `GET /api/crm/partners/{id}/contacts` - Get partner contacts

### Contacts
- `GET /api/crm/contacts` - List contacts
- `GET /api/crm/contacts/{id}` - Get contact
- `POST /api/crm/contacts` - Create contact
- `PUT /api/crm/contacts/{id}` - Update contact
- `DELETE /api/crm/contacts/{id}` - Delete contact

### Leads
- `GET /api/crm/leads` - List leads
- `GET /api/crm/leads/{id}` - Get lead
- `POST /api/crm/leads` - Create lead
- `PUT /api/crm/leads/{id}` - Update lead
- `POST /api/crm/leads/{id}/qualify` - Qualify lead to partner

### Opportunities
- `GET /api/crm/opportunities` - List opportunities
- `GET /api/crm/opportunities/{id}` - Get opportunity
- `POST /api/crm/opportunities` - Create opportunity
- `PUT /api/crm/opportunities/{id}` - Update opportunity

## Permissions

Module permissions follow the pattern `crm:<resource>:<action>`:

- `crm:partners:list` - List partners
- `crm:partners:read` - Read partner details
- `crm:partners:create` - Create partners
- `crm:partners:update` - Update partners
- `crm:partners:delete` - Delete partners
- `crm:contacts:*` - Contact permissions
- `crm:leads:*` - Lead permissions
- `crm:opportunities:*` - Opportunity permissions

## Domain Model

### Partner (Aggregate Root)

```python
@dataclass
class Partner(AggregateRoot):
    name: str
    partner_type: PartnerType  # INDIVIDUAL | COMPANY
    is_customer: bool
    is_supplier: bool
    email: Email | None
    phone: PhoneNumber | None
    # Address, tax info, etc.
```

### Contact (Aggregate Root)

```python
@dataclass
class Contact(AggregateRoot):
    partner_id: str  # References Partner
    first_name: str
    last_name: str
    email: Email
    phone: PhoneNumber | None
    is_primary: bool
```

### Lead (Aggregate Root)

```python
@dataclass
class Lead(AggregateRoot):
    name: str
    company: str | None
    email: Email
    status: LeadStatus  # NEW | CONTACTED | QUALIFIED | LOST
    score: int
```

### Opportunity (Aggregate Root)

```python
@dataclass
class Opportunity(AggregateRoot):
    partner_id: str
    name: str
    stage: OpportunityStage  # PROSPECTING | PROPOSAL | NEGOTIATION | WON | LOST
    amount: Decimal
    probability: int
    expected_close_date: date
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy serp_crm

# Linting
uv run ruff check serp_crm
```

## License

MIT License - See LICENSE file for details
