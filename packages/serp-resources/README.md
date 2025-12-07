# SERP Resources

Shared resources and value objects for SERP modules.

## Overview

This package provides common value objects and utilities that are used across multiple SERP modules. By centralizing these resources, we ensure consistency and avoid duplication.

## Value Objects

### Email

Email address with validation:

```python
from serp_resources import Email

email = Email("user@example.com")
print(email)  # user@example.com
```

### PhoneNumber

Phone number with basic validation:

```python
from serp_resources import PhoneNumber

phone = PhoneNumber("+1-555-123-4567")
print(phone)  # +15551234567
```

### Address

Physical address:

```python
from serp_resources import Address

address = Address(
    street="123 Main St",
    city="New York",
    state="NY",
    postal_code="10001",
    country="US"
)
```

### Money

Monetary value with currency:

```python
from serp_resources import Money
from decimal import Decimal

price = Money(Decimal("99.99"), "USD")
total = price + Money(Decimal("10.00"), "USD")
print(total)  # 109.99 USD
```

### TaxId

Tax identification number:

```python
from serp_resources import TaxId

tax_id = TaxId("123456789", "US")
print(tax_id)  # US-123456789
```

## Installation

```bash
uv add serp-resources
```

## Usage in Modules

```python
from serp_resources import Email, PhoneNumber, Address, Money, TaxId

# Use in your domain entities
@dataclass
class Customer(AggregateRoot):
    name: str
    email: Email
    phone: PhoneNumber | None = None
    billing_address: Address | None = None
```

## License

MIT License - See LICENSE file for details.
