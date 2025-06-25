import unittest
import time
from unittest.mock import MagicMock
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QCoreApplication
from ui.main_window import AtlasMainWindow

class ModulePerformanceTest(unittest.TestCase):
    def setUp(self):
        # Ensure a QApplication instance exists for Qt operations
        if QCoreApplication.instance() is None:
            self.app = QApplication([])
        else:
            self.app = QCoreApplication.instance()
        # Mock any dependencies that might cause issues during testing
        self.mock_meta_agent = MagicMock()
        self.mock_meta_agent.agent_manager = MagicMock()

    def test_module_initialization_performance(self):
        """Test the performance of initializing all modules in AtlasMainWindow."""
        start_time = time.time()
        # Initialize the main window with mocked dependencies
        main_window = AtlasMainWindow()
        # Force initialization of modules with the mocked meta_agent
        main_window._init_modules(meta_agent=self.mock_meta_agent)
        end_time = time.time()

        initialization_time = end_time - start_time
        print(f"Module initialization took {initialization_time:.3f} seconds")
        # Assert that initialization completes within an acceptable time frame
        self.assertLess(initialization_time, 2.0, "Module initialization took too long")

    def test_module_switching_performance(self):
        """Test the performance of switching between modules."""
        main_window = AtlasMainWindow()
        main_window._init_modules(meta_agent=self.mock_meta_agent)

        # Test switching between all modules
        module_names = list(main_window.modules.keys())
        start_time = time.time()
        for name in module_names * 10:  # Switch between modules 10 times each
            main_window._switch_module(name)
        end_time = time.time()

        switching_time = end_time - start_time
        total_switches = len(module_names) * 10
        avg_switch_time = switching_time / total_switches
        print(f"Total switching time for {total_switches} switches: {switching_time:.3f} seconds")
        print(f"Average switch time: {avg_switch_time:.3f} seconds")
        self.assertLess(avg_switch_time, 0.05, "Average module switch time is too slow")

    def test_language_change_performance(self):
        """Test the performance of changing language and updating UI."""
        main_window = AtlasMainWindow()
        main_window._init_modules(meta_agent=self.mock_meta_agent)

        start_time = time.time()
        for _ in range(10):  # Simulate changing language 10 times
            main_window.change_language()
        end_time = time.time()

        total_time = end_time - start_time
        avg_change_time = total_time / 10
        print(f"Total time for 10 language changes: {total_time:.3f} seconds")
        print(f"Average language change time: {avg_change_time:.3f} seconds")
        self.assertLess(avg_change_time, 0.2, "Average language change time is too slow")

if __name__ == '__main__':
    unittest.main()
