# serp-cli

> Developer CLI tools and code generators for SimpleERP modules

[![PyPI version](https://badge.fury.io/py/serp-cli.svg)](https://badge.fury.io/py/serp-cli)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)

## Overview

`serp-cli` provides developer tools for building SERP modules:

- **Code Generators**: Create entities, value objects, repositories, services
- **Module Scaffolding**: Initialize new module structure
- **Interactive Prompts**: Guided module creation
- **Template System**: Customizable Jinja2 templates
- **Validation**: Check module structure and configuration

## Installation

```bash
uv add serp-cli --dev
```

## Commands

### Module Commands

```bash
# Create a new module (interactive)
serp-cli create module

# Create with specific name
serp-cli create module my-inventory

# List installed modules
serp-cli list modules

# Validate module structure
serp-cli validate module ./my-module
```

### Entity Commands

```bash
# Create a new entity
serp-cli create entity Customer --module serp-crm

# Create entity with fields
serp-cli create entity Product \
    --module serp-inventory \
    --field name:str \
    --field price:Decimal \
    --field sku:str

# Generate entity with value objects
serp-cli create entity Order \
    --field customer_id:UUID \
    --field total:Money \
    --value-object Money
```

### Repository Commands

```bash
# Create repository for entity
serp-cli create repository CustomerRepository \
    --entity Customer \
    --module serp-crm

# Create with custom methods
serp-cli create repository ProductRepository \
    --entity Product \
    --method find_by_sku \
    --method find_in_stock
```

### Service Commands

```bash
# Create domain service
serp-cli create service PricingService \
    --type domain \
    --module serp-products

# Create application service
serp-cli create service CustomerService \
    --type application \
    --module serp-crm
```

### View Commands

```bash
# Create UI view
serp-cli create view CustomerList \
    --module serp-crm \
    --route /customers

# Create with permissions
serp-cli create view OrderDetails \
    --module serp-orders \
    --route /orders/:id \
    --permission orders.view
```

### Utility Commands

```bash
# Show module structure
serp-cli tree ./my-module

# Generate documentation
serp-cli docs generate

# Check dependencies
serp-cli check deps
```

## Interactive Mode

Run without arguments for interactive mode:

```bash
serp-cli create
```

This will prompt you for:
- What to create (module, entity, service, etc.)
- Name and configuration
- Optional features

## Templates

Templates are located in `serp_cli/templates/`:

```
templates/
├── entity.py.j2
├── value_object.py.j2
├── repository.py.j2
├── service.py.j2
├── view.tsx.j2
└── module/
    ├── __init__.py.j2
    ├── pyproject.toml.j2
    └── README.md.j2
```

### Custom Templates

Override templates by creating `~/.serp/templates/`:

```bash
mkdir -p ~/.serp/templates
cp /path/to/serp-cli/templates/entity.py.j2 ~/.serp/templates/
# Edit your custom template
```

## Examples

### Create a Complete Feature

```bash
# 1. Create entity
serp-cli create entity Invoice \
    --field number:str \
    --field customer_id:UUID \
    --field amount:Decimal \
    --field status:str

# 2. Create repository
serp-cli create repository InvoiceRepository \
    --entity Invoice

# 3. Create application service
serp-cli create service InvoiceService \
    --type application

# 4. Create API routes
serp-cli create routes InvoiceRoutes \
    --service InvoiceService

# 5. Create UI view
serp-cli create view InvoiceList \
    --route /invoices
```

## Development

```bash
# Clone and install
git clone https://github.com/simpleerp/serp.git
cd serp/packages/serp-cli
uv sync

# Run tests
uv run pytest

# Run CLI in dev mode
uv run python -m serp_cli.cli --help
```

## License

MIT License - see [LICENSE](../../LICENSE) for details
