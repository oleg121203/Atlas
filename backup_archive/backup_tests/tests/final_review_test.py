import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from ui.main_window import AtlasMainWindow


class FinalReviewTest(unittest.TestCase):
    def setUp(self):
        # Ensure a QApplication instance exists for Qt operations
        if QCoreApplication.instance() is None:
            self.app = QApplication([])
        else:
            self.app = QCoreApplication.instance()
        # Mock dependencies
        self.mock_meta_agent = MagicMock()
        self.mock_meta_agent.agent_manager = MagicMock()

    def test_main_window_initialization(self):
        """Test that AtlasMainWindow initializes correctly with all components."""
        main_window = AtlasMainWindow(meta_agent=self.mock_meta_agent)
        self.assertIsNotNone(main_window, "Main window should initialize")
        self.assertIsNotNone(main_window.sidebar, "Sidebar should be initialized")
        self.assertIsNotNone(main_window.topbar, "Topbar should be initialized")
        self.assertIsNotNone(
            main_window.central, "Central widget should be initialized"
        )
        self.assertIsNotNone(
            main_window.right_panel, "Right panel should be initialized"
        )
        self.assertIsNotNone(
            main_window.modules, "Modules dictionary should be initialized"
        )
        self.assertIsNotNone(main_window.event_bus, "Event bus should be initialized")
        self.assertIsNotNone(
            main_window.memory_manager, "Memory manager should be initialized"
        )

    def test_module_initialization_completeness(self):
        """Test that all expected modules are initialized in the main window."""
        main_window = AtlasMainWindow(meta_agent=self.mock_meta_agent)
        expected_modules = [
            "chat",
            "agents",
            "tasks",
            "plugins",
            "settings",
            "stats",
            "system",
        ]
        for module_name in expected_modules:
            self.assertIn(
                module_name,
                main_window.modules,
                f"Module {module_name} should be initialized",
            )
        self.assertTrue(
            hasattr(main_window, "self_improvement_module"),
            "SelfImprovement module should be initialized",
        )

    def test_ui_elements_responsiveness(self):
        """Test that UI elements are responsive and connected."""
        main_window = AtlasMainWindow(meta_agent=self.mock_meta_agent)
        # Check if sidebar actions are connected (indirectly via count of actions)
        sidebar_actions = main_window.sidebar.actions()
        self.assertGreater(
            len(sidebar_actions), 0, "Sidebar should have actions connected"
        )
        # Check if topbar elements are initialized
        self.assertIsNotNone(
            main_window.lang_combo, "Language combo box should be initialized"
        )
        self.assertIsNotNone(main_window.search_box, "Search box should be initialized")

    @patch("ui_qt.main_window.QTimer")
    def test_periodic_tasks_setup(self, mock_qtimer):
        """Test that periodic tasks like memory management are set up correctly."""
        mock_timer_instance = MagicMock()
        mock_qtimer.return_value = mock_timer_instance
        AtlasMainWindow(meta_agent=self.mock_meta_agent)
        mock_timer_instance.timeout.connect.assert_called_once()
        mock_timer_instance.start.assert_called_once_with(
            300000
        )  # 5 minutes for memory management

    def test_error_handling_robustness(self):
        """Test that the application handles initialization errors gracefully."""
        with (
            patch(
                "ui_qt.main_window.ChatModule",
                side_effect=Exception("ChatModule initialization failed"),
            ),
            patch(
                "ui_qt.main_window.TasksModule",
                side_effect=Exception("TasksModule initialization failed"),
            ),
        ):
            main_window = AtlasMainWindow(meta_agent=self.mock_meta_agent)
            self.assertIn(
                "chat", main_window.modules, "Chat module should have fallback"
            )
            self.assertIn(
                "tasks", main_window.modules, "Tasks module should have fallback"
            )

    def test_performance_metrics(self):
        """Test performance metrics to ensure no major regressions."""
        import time

        start_time = time.time()
        AtlasMainWindow(meta_agent=self.mock_meta_agent)
        initialization_time = time.time() - start_time
        self.assertLess(
            initialization_time,
            5.0,
            "Main window initialization should be under 5 seconds",
        )


if __name__ == "__main__":
    unittest.main()
