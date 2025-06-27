"""
Pytest configuration for Atlas tests.
"""

import os
import sys

import pytest

# Add Atlas root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def atlas_config():
    """Basic Atlas configuration for testing."""
    return {
        "test_mode": True,
        "debug": True
    }
