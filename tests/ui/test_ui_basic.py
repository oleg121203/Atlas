"""
Basic UI tests for macOS Atlas application.
"""

import os
from pathlib import Path

import pytest


@pytest.mark.ui
def test_ui_environment():
    """Test that UI test environment is configured correctly."""
    assert os.environ.get("ATLAS_UI_TEST") == "true"
    assert os.environ.get("ATLAS_PLATFORM") == "macos"


@pytest.mark.ui
def test_ui_modules_exist():
    """Test that UI module directories exist."""
    project_root = Path(__file__).parent.parent.parent

    # Check UI directories
    assert (project_root / "ui").exists()
    assert (project_root / "backup_ui_qt").exists()


@pytest.mark.ui
@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Skip GUI tests in CI")
def test_pyside6_import():
    """Test that PySide6 can be imported for GUI tests."""
    try:
        import PySide6  # noqa: F401

        assert True
    except ImportError:
        pytest.skip("PySide6 not available for GUI testing")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "ui"])
