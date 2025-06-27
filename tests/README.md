# Atlas Test Structure

This directory contains clean, well-structured tests for the Atlas project.

## Overview

- All legacy/problematic tests have been moved to `backup_archive/backup_tests/`
- This directory now contains only minimal, clean test files
- The test structure follows modern Python testing best practices

## Files

- `__init__.py` - Test package initialization
- `conftest.py` - Pytest configuration and fixtures
- `test_basic.py` - Basic smoke tests for Atlas functionality

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_basic.py

# Run with coverage
pytest tests/ --cov=. --cov-config=pyproject.toml
```

## Adding New Tests

When adding new tests:

1. Follow the naming convention `test_*.py`
2. Use descriptive test function names starting with `test_`
3. Use fixtures from `conftest.py` when needed
4. Keep tests simple and focused
5. Ensure tests pass ruff linting

## Guidelines

- Keep tests simple and maintainable
- Use clear assertions with descriptive messages
- Mock external dependencies appropriately
- Test both success and failure cases
- Maintain good test coverage

## Coverage Configuration

The code coverage configuration is defined in `pyproject.toml` in the project root:

- Coverage settings use the `[tool.coverage.*]` sections in `pyproject.toml`
- HTML reports are generated in `coverage_html_report/`
- Excludes test files, backup files, and other non-core code

## Legacy Tests

If you need to reference legacy test files, they are archived in:
- `backup_archive/backup_tests/tests/` - Original tests directory
- `backup_archive/backup_tests/scattered_tests/` - Tests from various locations
- `backup_archive/backup_tests/test_temp_generated_tools/` - Temporary test tools

These archived tests can be used as reference but should not be executed directly due to various issues and dependencies.
