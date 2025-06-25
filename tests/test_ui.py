"""
Test cases for the UI module of Atlas application.
"""

import unittest
from ui.main_window import MainWindow
from core.application import AtlasApplication

class TestUIComponents(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.app = AtlasApplication([])
        self.main_window = MainWindow()

    def test_main_window_initialization(self):
        """Test if the main window initializes correctly."""
        self.assertIsNotNone(self.main_window)
        self.assertTrue(hasattr(self.main_window, 'module_registry'))
        self.assertTrue(hasattr(self.main_window, 'initialize_ui'))

    def test_module_loading(self):
        """Test if modules are loaded correctly in the main window."""
        self.main_window.initialize_modules()
        self.assertGreater(len(self.main_window.module_registry.get_registered_modules()), 0)

if __name__ == '__main__':
    unittest.main()
