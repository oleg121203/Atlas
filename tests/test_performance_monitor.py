import unittest
import time
from performance_optimization.performance_monitor import PerformanceMonitor

class TestPerformanceMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = PerformanceMonitor()

    def test_start_stop_monitoring(self):
        """Test starting and stopping performance monitoring."""
        self.monitor.start_monitoring()
        time.sleep(1)  # Simulate some work
        metrics = self.monitor.stop_monitoring()
        self.assertIsInstance(metrics, dict)
        self.assertIn('start_cpu_percent', metrics)
        self.assertIn('end_cpu_percent', metrics)
        self.assertIn('duration', metrics)
        self.assertGreater(metrics['duration'], 0)

    def test_measure_response_time(self):
        """Test measuring response time for a function."""
        self.monitor.measure_response_time('test_function', 0.05)
        self.assertIn('response_times', self.monitor.metrics)
        self.assertIn('test_function', self.monitor.metrics['response_times'])
        self.assertEqual(self.monitor.metrics['response_times']['test_function'], 0.05)

    def test_generate_performance_report(self):
        """Test generating a performance report."""
        self.monitor.start_monitoring()
        self.monitor.measure_response_time('test_function', 0.05)
        time.sleep(1)
        self.monitor.stop_monitoring()
        report = self.monitor.generate_performance_report()
        self.assertIsInstance(report, dict)
        self.assertIn('date_generated', report)
        self.assertIn('cpu_usage', report)
        self.assertIn('memory_usage', report)
        self.assertIn('response_times', report)

    def test_identify_bottlenecks(self):
        """Test identifying performance bottlenecks."""
        self.monitor.measure_response_time('slow_function', 0.2)
        self.monitor.measure_response_time('fast_function', 0.05)
        bottlenecks = self.monitor.identify_bottlenecks(threshold=0.1)
        self.assertIsInstance(bottlenecks, list)
        self.assertEqual(len(bottlenecks), 1)
        self.assertTrue(bottlenecks[0].startswith('slow_function'))

    def test_optimize_performance(self):
        """Test suggesting optimizations for bottlenecks."""
        bottlenecks = ['slow_function: 0.2 seconds']
        optimizations = self.monitor.optimize_performance(bottlenecks)
        self.assertIsInstance(optimizations, dict)
        self.assertIn('slow_function', optimizations)
        self.assertIn('suggestion', optimizations['slow_function'])
        self.assertIn('potential_impact', optimizations['slow_function'])

if __name__ == '__main__':
    unittest.main()
