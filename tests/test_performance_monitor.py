import time
import unittest
from collections import deque
from unittest.mock import MagicMock, patch

# Import monitoring functions directly
from core.monitoring import (
    PERFORMANCE_METRICS,
    alert,
    get_performance_stats,
    initialize_monitoring,
    register_alert_handler,
    start_monitoring,
    stop_monitoring,
    track_performance,
)


class TestPerformanceMonitoring(unittest.TestCase):
    def setUp(self):
        # Clear performance metrics before each test
        PERFORMANCE_METRICS.clear()
        # Reset alert handlers
        self._alert_handlers = []

    def test_initialize_monitoring(self):
        with (
            patch(
                "core.monitoring.get_config", return_value={"monitoring_enabled": True}
            ),
            patch("core.monitoring.Thread") as mock_thread,
        ):
            result = initialize_monitoring()
            self.assertTrue(result)
            mock_thread.assert_called_once()

    def test_initialize_monitoring_disabled(self):
        # Reset the monitoring thread to None to simulate first initialization attempt
        with (
            patch(
                "core.monitoring.get_config", return_value={"monitoring_enabled": False}
            ),
            patch("core.monitoring._monitoring_thread", None),
        ):
            result = initialize_monitoring()
            self.assertFalse(result)

    def test_start_monitoring(self):
        with patch("core.monitoring.logger") as mock_logger:
            result = start_monitoring()
            self.assertTrue(result)
            mock_logger.info.assert_called_with("Starting monitoring system")

    def test_track_performance(self):
        component = "test_component"
        category = "screen_tools"
        duration_ms = 50.0
        details = {"test": "data"}

        with (
            patch("core.monitoring.time") as mock_time,
            patch("core.monitoring.alert") as mock_alert,
            patch("core.monitoring.logger") as mock_logger,
        ):
            mock_time.time.return_value = 1234567890.0
            track_performance(component, category, duration_ms, details)

            self.assertIn(component, PERFORMANCE_METRICS)
            self.assertEqual(len(PERFORMANCE_METRICS[component]), 1)
            metric = PERFORMANCE_METRICS[component][0]
            self.assertEqual(metric["timestamp"], 1234567890.0)
            self.assertEqual(metric["category"], category)
            self.assertEqual(metric["duration_ms"], duration_ms)
            self.assertEqual(metric["details"], details)
            mock_alert.assert_not_called()
            mock_logger.debug.assert_called_once()

    def test_track_performance_exceed_threshold(self):
        component = "test_component"
        category = "screen_tools"
        duration_ms = 150.0  # Exceeds 100ms threshold for screen_tools

        with (
            patch("core.monitoring.time", return_value=1234567890.0),
            patch("core.monitoring.alert") as mock_alert,
        ):
            track_performance(component, category, duration_ms)
            mock_alert.assert_called_once()

    def test_get_performance_stats(self):
        component = "test_component"
        category = "screen_tools"
        # Use deque directly to match type expectation
        PERFORMANCE_METRICS[component] = deque(
            [
                {
                    "timestamp": time.time(),
                    "category": category,
                    "duration_ms": 50.0,
                    "details": {},
                },
                {
                    "timestamp": time.time(),
                    "category": category,
                    "duration_ms": 100.0,
                    "details": {},
                },
                {
                    "timestamp": time.time(),
                    "category": category,
                    "duration_ms": 150.0,
                    "details": {},
                },
            ],
            maxlen=100,
        )

        stats = get_performance_stats(component)
        self.assertIsNotNone(stats)
        if stats is not None:
            self.assertEqual(stats["component"], component)
            self.assertEqual(stats["count"], 3)
            self.assertEqual(stats["average_ms"], 100.0)
            self.assertEqual(stats["min_ms"], 50.0)
            self.assertEqual(stats["max_ms"], 150.0)
            self.assertEqual(len(stats["last_10_measurements"]), 3)

    def test_get_performance_stats_empty(self):
        stats = get_performance_stats("non_existent_component")
        self.assertIsNone(stats)

    def test_register_alert_handler(self):
        handler = MagicMock()
        with (
            patch("core.monitoring._alert_handlers", self._alert_handlers),
            patch("core.monitoring.logger") as mock_logger,
        ):
            register_alert_handler(handler)
            self.assertIn(handler, self._alert_handlers)
            mock_logger.debug.assert_called_once()

    def test_alert(self):
        handler1 = MagicMock()
        handler2 = MagicMock()
        with (
            patch("core.monitoring._alert_handlers", [handler1, handler2]),
            patch("core.monitoring.logger") as mock_logger,
        ):
            alert("Test Title", "Test Message", {"test": "data"})
            handler1.assert_called_once_with(
                "Test Title", "Test Message", {"test": "data"}
            )
            handler2.assert_called_once_with(
                "Test Title", "Test Message", {"test": "data"}
            )
            mock_logger.warning.assert_called_once()

    def test_stop_monitoring(self):
        with (
            patch("core.monitoring._monitoring_active", True),
            patch("core.monitoring._monitoring_thread", MagicMock()),
            patch("core.monitoring.logger") as mock_logger,
        ):
            stop_monitoring()
            mock_logger.info.assert_called_with("Monitoring system stopped")


if __name__ == "__main__":
    unittest.main()
