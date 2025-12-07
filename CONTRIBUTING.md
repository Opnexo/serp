# Contributing to SimpleERP

Thank you for your interest in contributing to SimpleERP! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and professional in all interactions with the community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/serp.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `uv sync`

## Development Workflow

### Making Changes

1. Make your changes in your feature branch
2. Write or update tests as needed
3. Ensure all tests pass: `uv run pytest`
4. Format code: `uv run black .`
5. Lint code: `uv run ruff check .`
6. Commit your changes with clear messages

### Commit Messages

Follow the conventional commits specification:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Example: `feat(serp-core): add domain event base class`

### Pull Requests

1. Push your changes to your fork
2. Create a pull request against the `main` branch
3. Describe your changes clearly in the PR description
4. Link any related issues
5. Wait for review and address any feedback

## Code Standards

### Python

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public APIs
- Maintain 80%+ test coverage

### TypeScript

- Follow the project's ESLint configuration
- Use TypeScript strict mode
- Write JSDoc comments for public APIs

### Testing

- Write unit tests for new features
- Write integration tests for API endpoints
- Ensure all tests pass before submitting PR

## Project Structure

### Packages

- **serp-core**: Core functionality, no module-specific code
- **serp-shell**: API shell and runtime
- **serp-cli**: CLI tools

### Modules

- Follow DDD architecture
- Keep domain logic pure (no infrastructure dependencies)
- Use dependency injection

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion in GitHub Discussions
- Reach out to maintainers

Thank you for contributing! 🎉
