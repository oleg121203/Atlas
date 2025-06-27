"""
Basic smoke test to verify Atlas can import successfully.
"""


def test_atlas_imports():
    """Test that we can import basic Atlas modules."""
    try:
        # Test basic imports
        import core
        import main

        assert True, "Basic imports successful"
    except ImportError as e:
        raise AssertionError(f"Import failed: {e}") from e


def test_configuration():
    """Test basic configuration loading."""
    try:
        from core.config import get_config

        config = get_config()
        assert config is not None, "Config should not be None"
    except Exception as e:
        raise AssertionError(f"Config test failed: {e}") from e


if __name__ == "__main__":
    test_atlas_imports()
    test_configuration()
    print("✅ All basic tests passed!")
