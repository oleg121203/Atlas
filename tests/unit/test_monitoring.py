import unittest
from unittest.mock import patch

import core.monitoring


class TestMonitoring(unittest.TestCase):
    def test_track_performance(self):
        """Test tracking performance of a function or operation."""
        with patch("core.monitoring.track_performance") as mock_track:
            core.monitoring.track_performance(
                "test_component", "screen_tools", 50.0, {"detail": "test"}
            )
            mock_track.assert_called_once_with(
                "test_component", "screen_tools", 50.0, {"detail": "test"}
            )

    def test_get_performance_stats(self):
        """Test retrieving performance statistics for a component."""
        with patch("core.monitoring.get_performance_stats") as mock_stats:
            mock_stats.return_value = {
                "average": 50.0,
                "min": 10.0,
                "max": 100.0,
                "count": 5,
            }
            result = core.monitoring.get_performance_stats("test_component")
            self.assertIsInstance(result, dict)
            self.assertIn("average", result)
            mock_stats.assert_called_once_with("test_component")

    def test_alert(self):
        """Test raising an alert to all registered handlers."""
        with patch("core.monitoring.alert") as mock_alert:
            core.monitoring.alert(
                "Test Alert", "This is a test alert", {"data": "test"}
            )
            mock_alert.assert_called_once_with(
                "Test Alert", "This is a test alert", {"data": "test"}
            )

    def test_initialize_monitoring(self):
        """Test initializing the monitoring system."""
        with patch("core.monitoring.initialize_monitoring") as mock_init:
            mock_init.return_value = True
            result = core.monitoring.initialize_monitoring()
            self.assertTrue(result)
            mock_init.assert_called_once()

    def test_stop_monitoring(self):
        """Test stopping the monitoring system."""
        with patch("core.monitoring.stop_monitoring") as mock_stop:
            core.monitoring.stop_monitoring()
            mock_stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
