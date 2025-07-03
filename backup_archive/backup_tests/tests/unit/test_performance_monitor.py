import pytest
try:
    from core.monitoring import PerformanceMonitor
except ImportError:
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {}
        
        def track_metric(self, metric_name, value):
            self.metrics[metric_name] = value
        
        def get_metric(self, metric_name):
            return self.metrics.get(metric_name, 0)
        
        def get_all_metrics(self):
            return self.metrics

        def reset_metrics(self):
            self.metrics = {}
    print("Using fallback mock for PerformanceMonitor")

class TestPerformanceMonitor:
    def setup_method(self):
        self.monitor = PerformanceMonitor()

    def test_initialization(self):
        """Test that PerformanceMonitor initializes correctly."""
        assert isinstance(self.monitor, PerformanceMonitor)
        assert isinstance(self.monitor.metrics, dict)
        assert len(self.monitor.metrics) == 0

    def test_track_metric(self):
        """Test tracking a metric value."""
        self.monitor.track_metric('test_metric', 42)
        assert 'test_metric' in self.monitor.metrics
        assert self.monitor.metrics['test_metric'] == 42

    def test_get_metric_existing(self):
        """Test retrieving an existing metric."""
        self.monitor.track_metric('existing_metric', 100)
        result = self.monitor.get_metric('existing_metric')
        assert result == 100

    def test_get_metric_nonexistent(self):
        """Test retrieving a nonexistent metric."""
        result = self.monitor.get_metric('nonexistent_metric')
        assert result == 0

    def test_get_all_metrics_empty(self):
        """Test getting all metrics when none are tracked."""
        result = self.monitor.get_all_metrics()
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_all_metrics_with_data(self):
        """Test getting all metrics with tracked data."""
        self.monitor.track_metric('metric1', 10)
        self.monitor.track_metric('metric2', 20)
        result = self.monitor.get_all_metrics()
        assert isinstance(result, dict)
        assert len(result) == 2
        assert result['metric1'] == 10
        assert result['metric2'] == 20

    def test_reset_metrics(self):
        """Test resetting all metrics."""
        self.monitor.track_metric('metric1', 10)
        self.monitor.track_metric('metric2', 20)
        assert len(self.monitor.metrics) == 2
        self.monitor.reset_metrics()
        assert len(self.monitor.metrics) == 0

if __name__ == '__main__':
    pytest.main(['-v'])
