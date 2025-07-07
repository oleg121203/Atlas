"""
Global pytest configuration and fixtures for Atlas AI Assistant tests.
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure the project root is in the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["ATLAS_ENV"] = "test"
os.environ["ATLAS_PLATFORM"] = "macos"
os.environ["PYTHONPATH"] = str(project_root)


@pytest.fixture(scope="session")
def project_root_path():
    """Provide the project root path for tests."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def test_data_dir(project_root_path):
    """Provide the test data directory path."""
    test_data = project_root_path / "tests" / "data"
    test_data.mkdir(exist_ok=True)
    return test_data


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up the test environment for each test."""
    # Ensure test environment variables are set
    os.environ["ATLAS_ENV"] = "test"
    os.environ["ATLAS_PLATFORM"] = "macos"

    # Set up any test-specific configurations
    yield

    # Cleanup after test if needed
    pass


@pytest.fixture
def mock_home_directory(tmp_path):
    """Provide a temporary home directory for tests."""
    home_dir = tmp_path / "home"
    home_dir.mkdir()

    # Mock the home directory
    original_home = os.environ.get("HOME")
    os.environ["HOME"] = str(home_dir)

    yield home_dir

    # Restore original home directory
    if original_home:
        os.environ["HOME"] = original_home
    else:
        os.environ.pop("HOME", None)


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "ui: mark test as UI test")
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "macos: mark test as macOS specific")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file paths."""
    for item in items:
        # Add markers based on test file location
        if "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Mark tests as slow if they have certain patterns
        if any(
            keyword in item.name for keyword in ["slow", "benchmark", "performance"]
        ):
            item.add_marker(pytest.mark.slow)
