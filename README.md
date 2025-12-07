# SimpleERP (SERP) Platform

> A modular, plugin-based ERP platform built with Python and FastAPI

[![CI](https://github.com/simpleerp/serp/workflows/CI/badge.svg)](https://github.com/simpleerp/serp/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Overview

SimpleERP (SERP) is a modular ERP platform designed to enable:

- **Core Team**: Build and maintain the platform foundation
- **Community Developers**: Create industry-specific modules
- **End Users**: Compose their ERP from available modules

## Architecture

This monorepo contains:

### Core Packages

- **serp-core**: Base classes, DDD patterns, plugin system
- **serp-shell**: FastAPI application shell and runtime
- **serp-cli**: Developer CLI tools for scaffolding and code generation

### Official Modules

- **serp-users**: User management and authentication
- **serp-crm**: Customer relationship management
- **serp-invoicing**: Invoicing and billing

### UI Shell

- **ui-shell**: NextJS 14+ frontend application

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ (for UI shell)

### Installation

```bash
# Clone the repository
git clone https://github.com/simpleerp/serp.git
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

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Documentation

- [Architecture Guide](docs/architecture/)
- [Developer Guide](docs/guides/)
- [API Reference](docs/api/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Documentation](https://docs.simpleerp.dev)
- [Issue Tracker](https://github.com/simpleerp/serp/issues)
- [Discussions](https://github.com/simpleerp/serp/discussions)
