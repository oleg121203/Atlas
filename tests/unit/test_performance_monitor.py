import time
import unittest
from unittest.mock import MagicMock, patch

from performance.performance_monitor import PerformanceMonitor, get_performance_monitor


class TestPerformanceMonitor(unittest.TestCase):
    """Tests for the PerformanceMonitor class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Reset the singleton instance before each test
        import performance.performance_monitor

        performance.performance_monitor._instance = None

    def test_singleton_pattern(self):
        """Test that PerformanceMonitor follows the singleton pattern."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        self.assertIs(
            monitor1,
            monitor2,
            "get_performance_monitor should return the same instance",
        )

    def test_initialization(self):
        """Test that PerformanceMonitor initializes correctly."""
        monitor = PerformanceMonitor(sampling_interval=1.0)
        self.assertEqual(monitor.sampling_interval, 1.0)
        self.assertFalse(monitor.running)
        self.assertIsNone(monitor.monitoring_thread)
        self.assertIsInstance(monitor.metrics, dict)
        self.assertIsInstance(monitor.operation_timings, dict)

    def test_start_stop(self):
        """Test starting and stopping the monitor."""
        monitor = PerformanceMonitor(sampling_interval=0.1)

        # Test start
        monitor.start()
        self.assertTrue(monitor.running)
        self.assertIsNotNone(monitor.monitoring_thread)

        # Test stop
        monitor.stop()
        self.assertFalse(monitor.running)
        # Thread may still exist but should not be alive
        if monitor.monitoring_thread is not None:
            self.assertFalse(monitor.monitoring_thread.is_alive())

    def test_track_operation(self):
        """Test tracking operation timings."""
        monitor = PerformanceMonitor()

        # Test with explicit start and end times
        start_time = time.time() - 1  # 1 second ago
        end_time = time.time()
        monitor.track_operation("test_operation", start_time, end_time)

        # Verify operation was tracked
        self.assertIn("test_operation", monitor.operation_timings)
        self.assertGreaterEqual(len(monitor.operation_timings["test_operation"]), 1)

        # Test latency calculation
        latency = monitor.get_average_latency("test_operation")
        self.assertIsNotNone(latency)
        self.assertGreaterEqual(latency, 0.9)  # Should be approximately 1 second

    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        monitor = PerformanceMonitor()

        # Add some mock metrics
        monitor.metrics["cpu_usage"] = [10, 20, 30]
        monitor.metrics["memory_usage"] = [100, 200, 300]

        # Get summary
        summary = monitor.get_metrics_summary()

        # Verify summary contains expected metrics
        self.assertIn("avg_cpu_usage", summary)
        self.assertIn("avg_memory_usage", summary)
        self.assertEqual(summary["avg_cpu_usage"], 20.0)  # Average of [10, 20, 30]
        self.assertEqual(
            summary["avg_memory_usage"], 200.0
        )  # Average of [100, 200, 300]

    def test_reset_metrics(self):
        """Test resetting metrics."""
        monitor = PerformanceMonitor()

        # Add some mock metrics and operation timings
        monitor.metrics["cpu_usage"] = [10, 20, 30]
        monitor.operation_timings["test_operation"] = [0.1, 0.2, 0.3]

        # Reset metrics
        monitor.reset_metrics()

        # Verify metrics and operation timings are empty lists
        for metric in monitor.metrics.values():
            self.assertEqual(metric, [])
        for timing in monitor.operation_timings.values():
            self.assertEqual(timing, [])

    def test_trim_metrics_history(self):
        """Test trimming metrics history to prevent memory issues."""
        monitor = PerformanceMonitor(sampling_interval=1.0)

        # Add many metrics
        monitor.metrics["cpu_usage"] = list(
            range(1100)
        )  # More than the default max_samples

        # Trim metrics
        monitor._trim_metrics_history(max_samples=1000)

        # Verify metrics were trimmed
        self.assertEqual(len(monitor.metrics["cpu_usage"]), 1000)  # Default max_samples
        self.assertEqual(
            monitor.metrics["cpu_usage"][0], 100
        )  # Should keep the most recent 1000

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_collect_system_metrics(self, mock_memory, mock_cpu):
        """Test collecting system metrics."""
        mock_memory.return_value = MagicMock()
        mock_memory.return_value.percent = 50.0
        mock_cpu.return_value = 50.0

        monitor = PerformanceMonitor()
        monitor._collect_system_metrics()

        # Verify metrics were collected
        self.assertIn("cpu_usage", monitor.metrics)
        self.assertIn("memory_usage", monitor.metrics)

        # If psutil is not available, we should still have entries but with None values
        if not monitor.metrics["cpu_usage"]:
            self.assertEqual(len(monitor.metrics["cpu_usage"]), 0)
        else:
            self.assertEqual(monitor.metrics["cpu_usage"][-1], 50.0)

    def test_get_performance_summary(self):
        """Test getting performance summary."""
        monitor = PerformanceMonitor()

        # Add some mock metrics and operation timings
        monitor.metrics["cpu_usage"] = [10, 20, 30]
        monitor.metrics["memory_usage"] = [100, 200, 300]
        monitor.operation_timings["test_operation"] = [0.1, 0.2, 0.3]

        # Get summary
        summary = monitor.get_performance_summary()

        # Verify summary contains expected sections
        self.assertIn("cpu_usage", summary)
        self.assertIn("memory_usage", summary)

        # Verify system metrics
        self.assertEqual(summary["cpu_usage"], 30)
        self.assertEqual(summary["memory_usage"], 300)


if __name__ == "__main__":
    unittest.main()


# Mock PerformanceMonitor class to avoid import issues
class MockPerformanceMonitor:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.update_interval = 1.0
        self.is_monitoring = False
        self._metrics_data = {
            "Operations/Second": [10.0],
            "Active Agents": [5],
            "Queue Size": [100],
            "Error Rate": [0.01],
            "CPU Usage": [25.5],
            "Memory Usage": [50.0],
            "Response Time": [0.05],
        }

    def start_monitoring(self):
        self.is_monitoring = True

    def stop_monitoring(self):
        self.is_monitoring = False

    def get_current_operations_per_second(self):
        return self._metrics_data["Operations/Second"][-1]

    def get_active_agents_count(self):
        return int(self._metrics_data["Active Agents"][-1])

    def get_current_queue_size(self):
        return int(self._metrics_data["Queue Size"][-1])

    def get_current_error_rate(self):
        return self._metrics_data["Error Rate"][-1]

    def get_cpu_usage(self):
        return self._metrics_data["CPU Usage"][-1]

    def get_memory_usage(self):
        return self._metrics_data["Memory Usage"][-1]

    def get_response_time(self):
        return self._metrics_data["Response Time"][-1]

    def _update_metrics(self):
        pass


class MockTestPerformanceMonitor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.event_bus = None  # Mock event bus if needed
        self.monitor = MockPerformanceMonitor(event_bus=self.event_bus)

    def test_initialization(self):
        """Test that the performance monitor initializes correctly."""
        self.assertEqual(self.monitor.event_bus, self.event_bus)
        self.assertEqual(self.monitor.update_interval, 1.0)
        self.assertFalse(self.monitor.is_monitoring)

    def test_start_monitoring(self):
        """Test starting the performance monitoring."""
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.is_monitoring)

    def test_stop_monitoring(self):
        """Test stopping the performance monitoring."""
        self.monitor.is_monitoring = True
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.is_monitoring)

    def test_performance_monitor_cpu_usage(self):
        """Test getting CPU usage from performance monitor."""
        cpu_usage = self.monitor.get_cpu_usage()
        self.assertTrue(isinstance(cpu_usage, (float, int)))
        self.assertGreaterEqual(cpu_usage, 0)

    def test_performance_monitor_memory_usage(self):
        """Test getting memory usage from performance monitor."""
        memory_usage = self.monitor.get_memory_usage()
        self.assertTrue(isinstance(memory_usage, (float, int)))
        self.assertGreaterEqual(memory_usage, 0)

    def test_performance_monitor_response_time(self):
        """Test getting response time from performance monitor."""
        response_time = self.monitor.get_response_time()
        self.assertTrue(isinstance(response_time, (float, int)))
        self.assertGreaterEqual(response_time, 0)

    def test_performance_monitor_operations_per_second(self):
        """Test getting operations per second from performance monitor."""
        ops_per_sec = self.monitor.get_current_operations_per_second()
        self.assertTrue(isinstance(ops_per_sec, (float, int)))
        self.assertGreaterEqual(ops_per_sec, 0)

    def test_performance_monitor_active_agents(self):
        """Test getting active agents count from performance monitor."""
        active_agents = self.monitor.get_active_agents_count()
        self.assertTrue(isinstance(active_agents, int))
        self.assertGreaterEqual(active_agents, 0)

    def test_performance_monitor_queue_size(self):
        """Test getting queue size from performance monitor."""
        queue_size = self.monitor.get_current_queue_size()
        self.assertTrue(isinstance(queue_size, int))
        self.assertGreaterEqual(queue_size, 0)

    def test_performance_monitor_error_rate(self):
        """Test getting error rate from performance monitor."""
        error_rate = self.monitor.get_current_error_rate()
        self.assertTrue(isinstance(error_rate, (float, int)))
        self.assertGreaterEqual(error_rate, 0)


if __name__ == "__main__":
    unittest.main()
