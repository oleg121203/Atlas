# Atlas AI Assistant Tests

This directory contains the test suite for the Atlas AI Assistant application.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Global pytest configuration (in project root)
├── test_basic.py           # Basic functionality tests
├── data/                   # Test data and fixtures
│   └── README.md
└── ui/                     # UI-specific tests
    ├── __init__.py
    └── test_ui_basic.py
```

## Running Tests

### Basic Tests
```bash
# Run all tests
make test
# or
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_basic.py -v

# Run tests with specific markers
python -m pytest -m "ui" -v
python -m pytest -m "not slow" -v
```

### Coverage Reports
```bash
# Run tests with coverage
make test-cov
# or
python -m pytest tests/ --cov=core --cov-report=html --cov-report=term-missing

# Open HTML coverage report
open htmlcov/index.html
```

### VS Code Integration
Tests are configured to work seamlessly with VS Code:

1. **Test Explorer**: Tests appear in the VS Code Test Explorer panel
2. **Debug Support**: Use F5 to debug individual tests
3. **Coverage Gutters**: Install the Coverage Gutters extension to see line coverage in the editor

## Test Categories

### Markers
Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, multiple components)
- `@pytest.mark.ui` - UI-related tests (may require GUI)
- `@pytest.mark.slow` - Slow tests (excluded by default in quick runs)
- `@pytest.mark.macos` - macOS-specific tests
- `@pytest.mark.api` - API-related tests
- `@pytest.mark.performance` - Performance benchmarking tests

### Running Specific Categories
```bash
# Run only UI tests
python -m pytest -m "ui" -v

# Run everything except slow tests
python -m pytest -m "not slow" -v

# Run unit tests only
python -m pytest -m "unit" -v
```

## Test Configuration

### Environment Variables
Tests automatically set these environment variables:
- `ATLAS_ENV=test`
- `ATLAS_PLATFORM=macos`
- `ATLAS_UI_TEST=true` (for UI tests)

### Configuration Files
- `pytest.ini` - Main pytest configuration
- `pyproject.toml` - Additional pytest settings and coverage configuration
- `.coveragerc` - Coverage configuration
- `conftest.py` - Global fixtures and test setup

## Writing Tests

### Basic Test Example
```python
import pytest
from pathlib import Path

def test_basic_functionality():
    """Test basic functionality."""
    assert True

@pytest.mark.ui
def test_ui_component():
    """Test UI component functionality."""
    # UI-specific test code
    pass

@pytest.mark.slow
def test_performance_benchmark():
    """Test performance characteristics."""
    # Slow test code
    pass
```

### Using Fixtures
```python
def test_with_temp_directory(tmp_path):
    """Test using temporary directory fixture."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    assert test_file.read_text() == "test content"

def test_with_project_root(project_root_path):
    """Test using project root fixture."""
    assert (project_root_path / "pyproject.toml").exists()
```

## Continuous Integration

### Local CI Check
Run the full CI pipeline locally:
```bash
make ci-local
# or
./scripts/local_ci_check.sh
```

This runs:
1. Ruff linting
2. Code formatting check
3. Type checking (if available)
4. Tests with coverage
5. Security scan
6. Pre-commit hooks

### VS Code Tasks
Use VS Code tasks for common operations:
- `Ctrl+Shift+P` → "Tasks: Run Task"
- Choose from available tasks like "Pytest: Run All Tests"

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running tests from the project root
2. **Missing Dependencies**: Run `pip install -e .` to install the project in development mode
3. **Environment Issues**: Check that virtual environment is activated
4. **Coverage Not Working**: Ensure coverage package is installed: `pip install coverage pytest-cov`

### Debug Mode
To debug tests in VS Code:
1. Set breakpoints in your test or source code
2. Use "Python: Test with Pytest" debug configuration
3. Or right-click on a test and select "Debug Test"

## Best Practices

1. **Fast Tests**: Keep unit tests fast (< 1 second each)
2. **Isolated Tests**: Tests should not depend on each other
3. **Clear Names**: Use descriptive test function names
4. **Good Coverage**: Aim for > 80% code coverage
5. **Mock External Services**: Don't make real API calls in tests
6. **Use Fixtures**: Reuse common test setup with fixtures
