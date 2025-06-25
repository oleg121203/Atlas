import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QCoreApplication
from ui_qt.main_window import AtlasMainWindow

class ModuleErrorHandlingTest(unittest.TestCase):
    def setUp(self):
        # Ensure a QApplication instance exists for Qt operations
        if QCoreApplication.instance() is None:
            self.app = QApplication([])
        else:
            self.app = QCoreApplication.instance()
        # Mock dependencies to simulate failures
        self.mock_meta_agent = MagicMock()
        self.mock_meta_agent.agent_manager = MagicMock()

    @patch('ui_qt.main_window.ChatModule')
    @patch('ui_qt.main_window.AgentsModule')
    @patch('ui_qt.main_window.TasksModule')
    @patch('ui_qt.main_window.PluginsModule')
    @patch('ui_qt.main_window.SettingsModule')
    @patch('ui_qt.main_window.StatsModule')
    @patch('ui_qt.main_window.SystemControlModule')
    @patch('ui_qt.main_window.SelfImprovementCenter')
    def test_module_initialization_with_failures(self, mock_self_improvement, mock_system, mock_stats, mock_settings, mock_plugins, mock_tasks, mock_agents, mock_chat):
        """Test module initialization with simulated failures to ensure error handling works."""
        # Simulate failures for specific modules by raising exceptions
        mock_chat.side_effect = Exception("ChatModule initialization failed")
        mock_tasks.side_effect = Exception("TasksModule initialization failed")
        mock_settings.side_effect = Exception("SettingsModule initialization failed")
        mock_self_improvement.side_effect = Exception("SelfImprovementCenter initialization failed")

        # Initialize main window
        main_window = AtlasMainWindow()
        main_window._init_modules(meta_agent=self.mock_meta_agent)

        # Verify that all modules are initialized (or have fallbacks)
        self.assertIn("chat", main_window.modules, "Chat module should be initialized with fallback")
        self.assertIsInstance(main_window.modules["chat"], QWidget, "Chat module should have fallback widget")
        self.assertIn("agents", main_window.modules, "Agents module should be initialized")
        self.assertNotIsInstance(main_window.modules["agents"], QWidget, "Agents module should not be a fallback")
        self.assertIn("tasks", main_window.modules, "Tasks module should be initialized with fallback")
        self.assertIsInstance(main_window.modules["tasks"], QWidget, "Tasks module should have fallback widget")
        self.assertIn("plugins", main_window.modules, "Plugins module should be initialized")
        self.assertNotIsInstance(main_window.modules["plugins"], QWidget, "Plugins module should not be a fallback")
        self.assertIn("settings", main_window.modules, "Settings module should be initialized with fallback")
        self.assertIsInstance(main_window.modules["settings"], QWidget, "Settings module should have fallback widget")
        self.assertIn("stats", main_window.modules, "Stats module should be initialized")
        self.assertNotIsInstance(main_window.modules["stats"], QWidget, "Stats module should not be a fallback")
        self.assertIn("system", main_window.modules, "System module should be initialized")
        self.assertNotIsInstance(main_window.modules["system"], QWidget, "System module should not be a fallback")
        self.assertTrue(hasattr(main_window, 'self_improvement_module'), "SelfImprovement module should be initialized")
        self.assertIsInstance(main_window.self_improvement_module, QWidget, "SelfImprovement module should have fallback widget")

    def test_module_initialization_without_meta_agent(self):
        """Test module initialization without meta_agent to ensure fallback handling."""
        main_window = AtlasMainWindow()
        main_window._init_modules(meta_agent=None)

        # Verify that modules are initialized even without meta_agent
        self.assertIn("chat", main_window.modules, "Chat module should be initialized")
        self.assertIn("agents", main_window.modules, "Agents module should be initialized")
        self.assertIn("tasks", main_window.modules, "Tasks module should be initialized")
        self.assertIn("plugins", main_window.modules, "Plugins module should be initialized")
        self.assertIn("settings", main_window.modules, "Settings module should be initialized")
        self.assertIn("stats", main_window.modules, "Stats module should be initialized")
        self.assertIn("system", main_window.modules, "System module should be initialized")
        self.assertTrue(hasattr(main_window, 'self_improvement_module'), "SelfImprovement module should be initialized")

    @patch('ui_qt.main_window.PluginManager')
    def test_plugin_manager_connection_failure(self, mock_plugin_manager):
        """Test error handling when connecting PluginManager to modules fails."""
        mock_plugin_manager.side_effect = Exception("PluginManager initialization failed")
        main_window = AtlasMainWindow()
        main_window.plugin_manager = mock_plugin_manager
        main_window._init_modules(meta_agent=self.mock_meta_agent)

        # Verify that initialization continues despite PluginManager failure
        self.assertIn("chat", main_window.modules, "Chat module should be initialized")
        self.assertIn("agents", main_window.modules, "Agents module should be initialized")
        self.assertIn("tasks", main_window.modules, "Tasks module should be initialized")
        self.assertIn("plugins", main_window.modules, "Plugins module should be initialized")
        self.assertIn("settings", main_window.modules, "Settings module should be initialized")

if __name__ == '__main__':
    unittest.main()
