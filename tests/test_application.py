#!/usr/bin/env python3
"""
Tests for the Atlas Application core module.
"""

from unittest.mock import Mock, patch

from core.application import AtlasApplication


class TestAtlasApplication:
    """Test cases for the AtlasApplication class."""

    def test_init(self):
        """Test that AtlasApplication initializes correctly."""
        app = AtlasApplication()

        # Check that all core systems are initialized
        assert app.config is not None
        assert app.event_bus is not None
        assert app.module_registry is not None
        assert app.plugin_system is not None
        assert app.tool_manager is not None
        assert app.self_healing is not None
        assert app.main_window is None  # Should be None initially

    def test_start_headless(self):
        """Test that the application can start in headless mode."""
        app = AtlasApplication()

        # Mock the tool manager initialization
        app.tool_manager.initialize_all_tools = Mock()

        app.start()

        # Verify tool manager was initialized
        app.tool_manager.initialize_all_tools.assert_called_once()

    def test_shutdown(self):
        """Test that the application shuts down cleanly."""
        app = AtlasApplication()

        # Mock the systems to track shutdown calls
        app.plugin_system.shutdown = Mock()
        app.config.save = Mock()
        app.main_window = Mock()
        app.qt_app = Mock()

        app.shutdown()

        # Verify shutdown was called on systems
        app.plugin_system.shutdown.assert_called_once()
        app.config.save.assert_called_once()
        app.main_window.close.assert_called_once()
        app.qt_app.quit.assert_called_once()

    @patch("core.application.QApplication")
    def test_initialize_ui(self, mock_qapp):
        """Test UI initialization."""
        app = AtlasApplication()

        # Mock the main window import
        with patch("core.application.AtlasMainWindow") as mock_main_window:
            mock_window = Mock()
            mock_main_window.return_value = mock_window

            app.initialize_ui()

            # Verify UI components were created
            assert app.qt_app is not None
            assert app.main_window is not None

    def test_run_with_ui(self):
        """Test running the application with UI."""
        app = AtlasApplication()

        # Mock Qt components
        app.qt_app = Mock()
        app.qt_app.exec.return_value = 0
        app.main_window = Mock()

        result = app.run()

        # Verify the application ran successfully
        assert result == 0
        app.main_window.show.assert_called_once()
        app.qt_app.exec.assert_called_once()

    def test_initialize_core_systems(self):
        """Test core systems initialization."""
        app = AtlasApplication()

        # Mock system methods
        app.config.load = Mock()
        app.plugin_system.initialize = Mock()
        app.event_bus.subscribe = Mock()

        app._initialize_core_systems()

        # Verify systems were initialized
        app.config.load.assert_called_once()
        app.plugin_system.initialize.assert_called_once()

        # Verify event subscriptions
        assert app.event_bus.subscribe.call_count >= 2

    def test_error_handling_in_run(self):
        """Test error handling during application run."""
        app = AtlasApplication()

        # Mock Qt app to raise an error
        app.qt_app = Mock()
        app.qt_app.exec.side_effect = Exception("Test error")
        app.main_window = Mock()

        with patch("core.application.logger") as mock_logger:
            result = app.run()

            # Should return error code and log the error
            assert result == 1
            mock_logger.error.assert_called()

    def test_event_bus_integration(self):
        """Test that event bus is properly integrated."""
        app = AtlasApplication()

        # Mock event handlers
        handler_mock = Mock()
        app.event_bus.subscribe("test_event", handler_mock)

        # Publish event
        app.event_bus.publish("test_event", data="test")

        # Handler should be called
        handler_mock.assert_called()
