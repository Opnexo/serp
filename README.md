# SimpleERP (SERP) Platform

> A modular, plugin-based ERP platform built with Python and FastAPI

[![CI](https://github.com/simpleerp/serp/workflows/CI/badge.svg)](https://github.com/simpleerp/serp/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

> **Note:** The Opnexo platform is powered by the internal **SERP engine** and `serp-*` packages.  
> It was previously known as **SimpleERP (SERP)**. The technical namespace (`serp-*`) is kept for
> stability and backward compatibility.

## Overview

**Opnexo** is a modular ERP platform designed to enable:

- **Core Team**: Build and maintain the platform foundation
- **Community Developers**: Create industry-specific modules
- **End Users**: Compose their ERP from available modules

The platform architecture is built around a plugin-based, domain-driven design, allowing you to
add or replace modules without changing the core.

## Architecture

This monorepo contains the core **SERP engine** and official modules that power the Opnexo platform.

### Core Packages (`serp-*`)

- **serp-core** – Base classes, DDD patterns, plugin system
- **serp-shell** – FastAPI application shell and runtime
- **serp-cli** – Developer CLI tools for scaffolding and code generation

### Official Modules

- **serp-users** – User management and authentication
- **serp-crm** – Customer relationship management
- **serp-invoicing** – Invoicing and billing

### UI Shell

- **ui-shell** – Next.js 14+ frontend application for the Opnexo web UI

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 22+ (for UI shell)

### Installation

```bash
# Clone the repository
git clone https://github.com/opnexo/serp.git
cd serp

# Install Python dependencies
uv sync

# Install UI dependencies
cd ui-shell
npm install
cd ..

# Run tests
uv run pytest

# Start development servers
uv run serp dev          # Backend (http://localhost:8000)
cd ui-shell && npm run dev  # Frontend (http://localhost:3000)
```

## Development

### Workspace Structure

```
serp/
├── packages/           # Core platform packages
├── modules/           # Official modules
├── ui-shell/          # NextJS frontend
├── docs/              # Documentation
└── scripts/           # Build and release scripts
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests for specific package
uv run pytest packages/serp-core

# Run with coverage
uv run pytest --cov=packages --cov=modules
```

### Building Packages

```bash
# Build all packages
./scripts/build-all.sh

# Build specific package
cd packages/serp-core
uv build
```

## Contributing

We welcome contributions to the Opnexo platform!

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on development workflow, coding standards,
and how to propose new modules.

## Documentation

- [Architecture Guide](docs/architecture/)
- [Developer Guide](docs/guides/)
- [API Reference](docs/api/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links
- Product Name: Opnexo Platform
- [Documentation](https://docs.opnexo.dev)
- [Issue Tracker](https://github.com/opnexo/serp/issues)
- [Discussions](https://github.com/opnexo/serp/discussions)
- [Twitter](https://twitter.com/opnexodev)