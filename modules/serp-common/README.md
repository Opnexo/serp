# SERP Common Module

Shared entities, value objects, and UI components used across SERP modules.

## Features

- **Address Management**: CRUD operations for addresses with UI components
- **Shared Value Objects**: Reusable domain primitives (via serp-resources)
- **Common UI Components**: Address picker, country selector, etc.

## Database Schema

This module uses the PostgreSQL schema `common` for its tables.

## Installation

```bash
pip install -e .
```

## Usage

```python
from serp_common import AddressService, AddressDTO

# Create address service
service = AddressService(repository)

# Create an address
address = await service.create_address(AddressCreateDTO(
    label="Main Office",
    street="123 Main St",
    city="New York",
    country="US",
    postal_code="10001"
))
```

## API Endpoints

- `GET /api/common/addresses` - List addresses
- `POST /api/common/addresses` - Create address
- `GET /api/common/addresses/{id}` - Get address
- `PUT /api/common/addresses/{id}` - Update address
- `DELETE /api/common/addresses/{id}` - Delete address

## Permissions

- `common:addresses:list` - View addresses
- `common:addresses:read` - View address details
- `common:addresses:create` - Create addresses
- `common:addresses:update` - Update addresses
- `common:addresses:delete` - Delete addresses
