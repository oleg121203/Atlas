import unittest
import time
import pandas as pd
from monitoring.system_monitor import SystemMonitor

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = SystemMonitor(interval=1)

    def test_collect_metrics(self):
        """Test collecting system metrics."""
        metrics = self.monitor.collect_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn('timestamp', metrics)
        self.assertIn('cpu_percent', metrics)
        self.assertIn('memory_used', metrics)
        self.assertIn('disk_percent', metrics)

    def test_get_metrics_dataframe(self):
        """Test converting collected metrics to DataFrame."""
        self.monitor.collect_metrics()
        df = self.monitor.get_metrics_dataframe()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertIn('cpu_percent', df.columns)

    def test_check_system_health(self):
        """Test checking system health based on metrics."""
        self.monitor.collect_metrics()
        health_status = self.monitor.check_system_health()
        self.assertIsInstance(health_status, dict)
        self.assertIn('overall_status', health_status)
        self.assertIn(health_status['overall_status'], ['Healthy', 'Critical', 'Unknown'])

    def test_alert_on_threshold(self):
        """Test generating alerts when metrics exceed thresholds."""
        self.monitor.collect_metrics()
        thresholds = {'cpu_percent': 0, 'memory_percent': 0}  # Very low thresholds to trigger alerts
        alerts = self.monitor.alert_on_threshold(thresholds)
        self.assertIsInstance(alerts, list)
        self.assertGreater(len(alerts), 0)  # Should have at least one alert due to low thresholds

    def test_start_stop_monitoring(self):
        """Test starting and stopping the monitoring process."""
        # Start monitoring in a separate thread or process if needed, but for simplicity, just check state
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.is_running)
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.is_running)

if __name__ == '__main__':
    unittest.main()
