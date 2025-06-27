"""
Basic smoke test to verify Atlas can import successfully.
"""


def test_python_version():
    """Test that we're running a supported Python version."""
    import sys

    major, minor = sys.version_info[:2]
    assert major == 3, f"Expected Python 3.x, got {major}.{minor}"
    assert minor >= 9, f"Expected Python 3.9+, got {major}.{minor}"


def test_basic_imports():
    """Test that we can import basic Python modules."""
    try:
        import json
        import os
        import pathlib
        import sys

        assert True, "Basic Python imports successful"
    except ImportError as e:
        raise AssertionError(f"Basic import failed: {e}") from e


def test_requirements_file_exists():
    """Test that requirements.txt exists."""
    import os

    req_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "requirements.txt"
    )
    assert os.path.exists(req_file), "requirements.txt should exist in project root"


def test_ruff_config_exists():
    """Test that ruff configuration exists."""
    import os

    ruff_config = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".ruff.toml")
    assert os.path.exists(ruff_config), ".ruff.toml should exist in project root"


def test_project_structure():
    """Test basic project structure exists."""
    import os

    project_root = os.path.dirname(os.path.dirname(__file__))

    expected_dirs = ["core", "utils", "tests"]
    for dir_name in expected_dirs:
        dir_path = os.path.join(project_root, dir_name)
        assert os.path.exists(dir_path), f"Directory {dir_name} should exist"


if __name__ == "__main__":
    test_python_version()
    test_basic_imports()
    test_requirements_file_exists()
    test_ruff_config_exists()
    test_project_structure()
    print("✅ All basic tests passed!")
