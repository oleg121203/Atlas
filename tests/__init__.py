"""
Tests for the Atlas AI Assistant application.

This directory contains all unit tests, integration tests, and test utilities.
"""

# Test configuration
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["ATLAS_PLATFORM"] = "macos"
os.environ["ATLAS_ENV"] = "test"
