"""
Test cases for Atlas Module System.
"""

import unittest
from unittest.mock import MagicMock

from core.module_system import ModuleRegistry


class TestModuleSystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.module_registry = ModuleRegistry()

    def test_module_registration(self):
        """Test module registration and retrieval."""
        mock_module = MagicMock()
        module_name = "test_module"

        # Test registration
        self.module_registry.register_module(module_name, mock_module)
        self.assertIn(module_name, self.module_registry.modules)

        # Test retrieval
        self.assertEqual(self.module_registry.get_module(module_name), mock_module)

    def test_module_duplicate_registration(self):
        """Test that duplicate module registration raises error."""
        mock_module = MagicMock()
        module_name = "test_module"

        self.module_registry.register_module(module_name, mock_module)
        self.assertRaises(
            ValueError, self.module_registry.register_module, module_name, mock_module
        )

    def test_get_nonexistent_module(self):
        """Test getting nonexistent module."""
        self.assertRaises(
            KeyError, self.module_registry.get_module, "nonexistent_module"
        )


if __name__ == "__main__":
    unittest.main()
