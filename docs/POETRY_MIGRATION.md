# Poetry Migration Guide

This project now supports both traditional setuptools and Poetry for dependency management.

## Using Poetry (Recommended)

### Installation

Install Poetry if you haven't already:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Setup Development Environment

```bash
# Install all dependencies including dev dependencies
poetry install

# Install only production dependencies
poetry install --only main

# Install with extras
poetry install --extras "data plugins"
```

### Common Commands

```bash
# Run the application
poetry run interference_calculator

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=interference_calculator

# Build documentation
cd docs/api && poetry run make html

# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8 interference_calculator/

# Type checking
poetry run mypy interference_calculator/

# Add new dependency
poetry add package-name

# Add dev dependency
poetry add --group dev package-name

# Update dependencies
poetry update
```

## Using setuptools (Legacy Support)

The project maintains backward compatibility with setuptools.

```bash
# Install in development mode
pip install -e .

# Install with extras
pip install -e ".[data]"

# Run tests
pytest

# Build distribution
python setup.py sdist bdist_wheel
```

## Dependency Groups

- **main**: Core runtime dependencies
- **dev**: Development tools (pytest, sphinx, black, etc.)
- **extras**:
  - `data`: requests for data fetching
  - `plugins`: PyYAML for plugin system

## Lock File

Poetry generates `poetry.lock` to ensure reproducible builds. This file should be committed to version control.

## CI/CD Integration

The project's CI/CD pipelines support both installation methods. Poetry is preferred for new setups.

## Migration Notes

- `setup.py` is kept for backward compatibility
- `pyproject.toml` now contains full Poetry configuration
- Both `pip install` and `poetry install` work correctly
- Dependencies are synchronized between both systems
