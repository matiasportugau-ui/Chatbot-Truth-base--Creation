# Contributing to AI Project Files Organizer Agent

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

5. Install pre-commit hooks:

```bash
pre-commit install
```

## Development Workflow

1. Create a feature branch from `develop`
2. Make your changes
3. Run tests: `pytest`
4. Run linting: `ruff check .`
5. Run formatting: `black .`
6. Commit your changes
7. Push to your fork
8. Create a Pull Request

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Keep functions focused and small
- Write tests for new features

## Testing

Run tests with:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=ai_files_organizer --cov-report=html
```

## Pull Request Process

1. Update CHANGELOG.md
2. Update documentation if needed
3. Ensure all tests pass
4. Ensure code is properly formatted
5. Request review

## Code of Conduct

Please be respectful and professional in all interactions.
