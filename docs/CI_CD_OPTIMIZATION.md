# CI/CD Optimization Guide

This document describes the enhanced CI/CD pipeline for Interference Calculator.

## Overview

The project now includes a comprehensive CI/CD pipeline with:
- Code quality checks (flake8, black, isort, mypy)
- Multi-platform testing matrix
- Performance regression detection
- Documentation build verification
- Security scanning
- Automated dependency updates (Dependabot)

## Enhanced CI Pipeline

### Workflow: `.github/workflows/ci-enhanced.yml`

Triggers on:
- Push to `main` or `develop` branches
- Pull requests to `main`

#### Jobs

1. **Code Quality (lint)**
   - flake8 linting
   - Black code formatting check
   - isort import sorting check
   - mypy type checking

2. **Test Matrix (test)**
   - Python versions: 3.9, 3.10, 3.11, 3.12
   - Operating systems: Ubuntu, Windows, macOS
   - Coverage reporting to Codecov

3. **Performance Tests (performance)**
   - Runs performance benchmarks
   - Detects performance regressions
   - Baseline comparison (future enhancement)

4. **Documentation (docs)**
   - Builds Sphinx API documentation
   - Verifies successful build
   - Checks HTML output

5. **Security Scan (security)**
   - Dependency vulnerability check
   - Safety scan for known CVEs

## Dependabot Configuration

### File: `.github/dependabot.yml`

Automatically creates pull requests for:

**Python Dependencies:**
- Weekly updates (Mondays at 09:00 Asia/Shanghai)
- Up to 10 PRs open simultaneously
- Labels: `dependencies`, `python`

**GitHub Actions:**
- Weekly updates (Mondays at 09:00 Asia/Shanghai)
- Up to 5 PRs open simultaneously
- Labels: `ci/cd`, `dependencies`

## Local Development Tools

Install development dependencies:

```bash
# Using pip
pip install flake8 black isort mypy pytest pytest-cov

# Using Poetry (recommended)
poetry install --with dev
```

### Run Locally

```bash
# Linting
flake8 interference_calculator/ tests/
black --check interference_calculator/ tests/
isort --check-only interference_calculator/ tests/
mypy interference_calculator/

# Testing
pytest tests/ --cov=interference_calculator

# All checks
./scripts/run_all_checks.sh  # (create this script if needed)
```

## Code Quality Standards

### flake8
- Max line length: 88 characters
- Ignore: E203 (whitespace before ':'), W503 (line break before binary operator)
- Special handling for long UI files

### Black
- Line length: 88
- Target Python versions: 3.9-3.12
- Automatic formatting enforcement

### isort
- Profile: black compatible
- Multi-line output: 3
- Trailing commas enabled

### mypy
- Python version: 3.9
- Strict mode with practical overrides for UI components
- Type checking for core modules

## Coverage Reporting

Coverage is uploaded to Codecov from:
- Python 3.11 on Ubuntu
- Flagged as `unittests`
- Failure is non-blocking (`fail_ci_if_error: false`)

## Future Enhancements

Potential improvements:
1. Store performance baselines and compare
2. Add mutation testing
3. Integration test suite
4. Docker-based testing environment
5. Automated release notes generation
6. Branch protection rules integration

## Troubleshooting

### CI Failures

If CI fails on code quality checks:

```bash
# Auto-fix formatting
black interference_calculator/ tests/
isort interference_calculator/ tests/

# Check remaining issues
flake8 interference_calculator/ tests/
mypy interference_calculator/
```

### Dependabot Not Creating PRs

Check:
1. Repository settings allow automated PRs
2. No existing open PRs for same dependency
3. Reviewer has write access

### Slow CI Runs

Optimization tips:
1. Use caching for dependencies
2. Parallelize independent jobs
3. Skip unnecessary steps on docs-only changes
4. Use faster runners if available
