#!/usr/bin/env python3
"""
Tests for the Self-Healing System core module.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

# Ensure the parent directory is in the path so we can import from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.self_healing import SelfHealingSystem


class TestSelfHealingSystem(unittest.TestCase):
    """Tests for the SelfHealingSystem class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Mock event bus for tests
        self.event_bus = MagicMock()
        self.self_healing = SelfHealingSystem(self.event_bus)

    def test_initialization(self):
        """Test that SelfHealingSystem initializes correctly."""
        self.assertEqual(self.self_healing.event_bus, self.event_bus)
        self.assertEqual(self.self_healing.diagnostic_results, {})
        self.assertEqual(self.self_healing.recovery_attempts, {})
        self.assertEqual(self.self_healing.max_recovery_attempts, 3)

    def test_diagnose_system(self):
        """Test running system diagnostics."""
        result = self.self_healing.diagnose_system()
        self.assertIsInstance(result, dict)
        self.assertIn("modules", result)
        self.assertIn("plugins", result)
        self.assertIn("ui_components", result)
        self.assertIn("configurations", result)
        self.assertIn("dependencies", result)
        self.assertIn("system_health", result)

    def test_restart_module(self):
        """Test requesting a module restart."""
        module_name = "test_module"
        self.self_healing.restart_module(module_name)
        self.event_bus.publish.assert_called_with(
            "module_restart_requested", module_name=module_name
        )

    def test_handle_error(self):
        """Test handling a system error event."""
        error = Exception("Test error")
        self.self_healing.handle_error(error=error)
        # Just verify no exception is raised, as the method currently logs the error
        self.assertTrue(True)

    def test_handle_module_error(self):
        """Test handling a module error event."""
        error = str(Exception("Test module error"))
        module_name = "test_module"
        self.self_healing.handle_module_error(module_name=module_name, error=error)
        # Verify the event was published for module restart
        self.event_bus.publish.assert_called_with(
            "module_restart_requested", module_name=module_name
        )


if __name__ == "__main__":
    unittest.main()
