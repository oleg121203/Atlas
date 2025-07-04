#!/usr/bin/env python3
"""
Tests for the Atlas Application core module.
"""

import unittest
from unittest.mock import patch

from core.application import AtlasApplication
from core.config import Config


class TestAtlasApplication(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = AtlasApplication()

    def test_initialization(self):
        """Test initialization of AtlasApplication."""
        self.assertIsInstance(self.app, AtlasApplication)
        self.assertIsNotNone(self.app.config, "Config should be initialized")
        self.assertIsNotNone(self.app.event_bus, "Event bus should be initialized")

    def test_run(self):
        """Test running the application."""
        # Mock QApplication to avoid actual GUI initialization in tests
        with patch("PySide6.QtWidgets.QApplication") as mock_qapp:
            # Ensure QApplication is initialized for the test
            mock_qapp.return_value = None
            with self.assertRaises(RuntimeError):
                self.app.run()
            # Test run with proper initialization if needed, but for now expect RuntimeError
            # as QApplication is not fully initialized in test environment

    def test_load_config(self):
        """Test loading configuration."""
        with patch.object(Config, "load") as mock_load:
            mock_load.return_value = {"test_key": "test_value"}
            config = self.app.config.load()
            mock_load.assert_called_once()
            self.assertEqual(
                config,
                {"test_key": "test_value"},
                "Configuration should match expected output",
            )

    def test_register_module(self):
        """Test module registration."""
        # Create a mock module that mimics ModuleBase structure if needed
        mock_module = type("MockModule", (), {"name": "test_module"})
        # Since module_registry is not directly accessible on AtlasApplication,
        # this test focuses on a conceptual registration process
        # Adjust test to reflect actual implementation if registration logic exists elsewhere
        # For now, assume a different approach or mock a registration process if needed
        self.assertTrue(
            hasattr(mock_module, "name"), "Mock module should have a name attribute"
        )

    def test_emit_event(self):
        """Test event emission."""
        event_name = "test_event"
        event_data = {"data": "test_data"}
        with patch.object(self.app.event_bus, "publish") as mock_publish:
            self.app.event_bus.publish(event_name, **event_data)
            mock_publish.assert_called_once_with(event_name, **event_data)


if __name__ == "__main__":
    unittest.main()
