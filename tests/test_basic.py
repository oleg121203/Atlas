"""
Basic test to verify the test setup works correctly.
"""

import os
import sys
from pathlib import Path

# Test imports
import pytest


def test_environment_setup():
    """Test that the test environment is set up correctly."""
    assert os.environ.get("ATLAS_PLATFORM") == "macos"
    assert os.environ.get("ATLAS_ENV") == "test"


def test_project_structure():
    """Test that the project structure is as expected."""
    project_root = Path(__file__).parent.parent

    # Check main directories exist
    assert (project_root / "atlas").exists()
    assert (project_root / "core").exists()
    assert (project_root / "ui").exists()
    assert (project_root / "tools").exists()
    assert (project_root / "utils").exists()

    # Check main files exist
    assert (project_root / "main.py").exists()
    assert (project_root / "pyproject.toml").exists()


def test_python_path():
    """Test that the Python path is correctly configured."""
    project_root = Path(__file__).parent.parent
    assert str(project_root) in sys.path


@pytest.mark.skipif(not os.path.exists("./app/main.py"), reason="App main.py not found")
def test_app_main_exists():
    """Test that the app main module exists."""
    assert Path("./app/main.py").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
