"""
Performance Monitor Module

This module provides performance monitoring for the Atlas application.
"""

import logging
import time
import tracemalloc
from typing import Any, Dict, List, Optional

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    TRACEMALLOC_AVAILABLE = True
except ImportError:
    TRACEMALLOC_AVAILABLE = False

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """A class for monitoring performance metrics of the Atlas application."""

    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self.start_time: float = time.time()
        if PSUTIL_AVAILABLE:
            try:
                self.process: Optional["psutil.Process"] = psutil.Process()
            except Exception as e:
                logger.error(f"Failed to initialize process for monitoring: {e}")
                self.process = None
        else:
            self.process = None

        # Initialize metrics
        self._metrics["CPU Usage"] = []
        self._metrics["Memory Usage"] = []
        self._metrics["Response Time"] = []
        self._metrics["Operations/sec"] = []
        self._metrics["Active Agents"] = []
        self._metrics["Queue Size"] = []
        self._metrics["Error Rate"] = []

    def record_metric(self, metric_name: str, value: float) -> None:
        """Record a performance metric.

        Args:
            metric_name (str): The name of the metric.
            value (float): The value of the metric.
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        self._metrics[metric_name].append(value)

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage.

        Returns:
            float: CPU usage percentage.
        """
        if self.process:
            try:
                cpu_percent = self.process.cpu_percent(interval=1)
                self.record_metric("CPU Usage", cpu_percent)
                return cpu_percent
            except Exception as e:
                logger.error(f"Error getting CPU usage: {e}")
                return 0.0
        return 0.0

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB.

        Returns:
            float: Memory usage in MB.
        """
        if self.process:
            try:
                mem_info = self.process.memory_info()
                mem_mb = mem_info.rss / (1024 * 1024)  # Convert to MB
                self.record_metric("Memory Usage", mem_mb)
                return mem_mb
            except Exception as e:
                logger.error(f"Error getting memory usage: {e}")
                return 0.0
        return 0.0

    def get_response_time(self) -> float:
        """Get simulated response time in milliseconds.

        Returns:
            float: Response time in milliseconds.
        """
        # Placeholder for actual response time measurement
        response_time = 50.0  # Simulated value
        self.record_metric("Response Time", response_time)
        return response_time

    def get_operations_per_second(self) -> float:
        """Get simulated operations per second.

        Returns:
            float: Operations per second.
        """
        # Placeholder for actual operations per second measurement
        ops_per_sec = 100.0  # Simulated value
        self.record_metric("Operations/sec", ops_per_sec)
        return ops_per_sec

    def get_active_agents(self) -> float:
        """Get simulated number of active agents.

        Returns:
            float: Number of active agents.
        """
        # Placeholder for actual active agents count
        active_agents = 5.0  # Simulated value
        self.record_metric("Active Agents", active_agents)
        return active_agents

    def get_queue_size(self) -> float:
        """Get simulated queue size.

        Returns:
            float: Queue size.
        """
        # Placeholder for actual queue size measurement
        queue_size = 10.0  # Simulated value
        self.record_metric("Queue Size", queue_size)
        return queue_size

    def get_error_rate(self) -> float:
        """Get simulated error rate percentage.

        Returns:
            float: Error rate percentage.
        """
        # Placeholder for actual error rate measurement
        error_rate = 0.5  # Simulated value
        self.record_metric("Error Rate", error_rate)
        return error_rate

    def get_average_metric(self, metric_name: str, window: int = 10) -> float:
        """Get the average of a metric over a specified window of recent values.

        Args:
            metric_name (str): The name of the metric.
            window (int): The number of recent values to average over.

        Returns:
            float: The average value of the metric over the window.
        """
        if metric_name in self._metrics and self._metrics[metric_name]:
            recent_values = self._metrics[metric_name][-window:]
            return sum(recent_values) / len(recent_values)
        return 0.0

    def start_memory_tracing(self) -> None:
        """Start tracing memory allocations if tracemalloc is available."""
        if TRACEMALLOC_AVAILABLE:
            tracemalloc.start()
            logger.info("Memory tracing started")
        else:
            logger.warning("tracemalloc not available, memory tracing not started")

    def stop_memory_tracing(self) -> None:
        """Stop tracing memory allocations if tracemalloc is available."""
        if TRACEMALLOC_AVAILABLE:
            tracemalloc.stop()
            logger.info("Memory tracing stopped")
        else:
            logger.warning("tracemalloc not available, memory tracing not stopped")

    def get_memory_snapshot(self) -> Optional[List[Any]]:
        """Get a snapshot of current memory allocations.

        Returns:
            Optional[List[Any]]: List of memory allocation statistics if tracemalloc is available, else None.
        """
        if TRACEMALLOC_AVAILABLE:
            snapshot = tracemalloc.take_snapshot()
            return snapshot.filter_traces(
                (
                    tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
                    tracemalloc.Filter(False, "<unknown>"),
                )
            ).statistics("lineno")
        return None

    def get_metrics_history(self) -> Dict[str, List[float]]:
        """Get the full history of recorded metrics.

        Returns:
            Dict[str, List[float]]: Dictionary of metric names to their historical values.
        """
        return self._metrics

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self._metrics.clear()
        logger.info("Performance metrics cleared")

    def get_latest_response_time(self) -> float:
        """Get the latest response time metric.

        Returns:
            float: Latest response time in seconds, or 0.0 if not available.
        """
        return (
            self._metrics.get("Response Time", [0.0])[-1]
            if "Response Time" in self._metrics
            else 0.0
        )

    def get_current_operations_per_second(self) -> float:
        """Get the operations per second metric.

        Returns:
            float: Operations per second, or 0.0 if not available.
        """
        ops_key = "Operations/sec"
        return (
            self._metrics.get(ops_key, [0.0])[-1] if ops_key in self._metrics else 0.0
        )

    def get_active_agents_count(self) -> int:
        """Get the number of active agents.

        Returns:
            int: Number of active agents, or 0 if not available.
        """
        return (
            int(self._metrics.get("Active Agents", [0])[-1])
            if "Active Agents" in self._metrics
            else 0
        )

    def get_current_queue_size(self) -> int:
        """Get the current queue size.

        Returns:
            int: Current queue size, or 0 if not available.
        """
        return (
            int(self._metrics.get("Queue Size", [0])[-1])
            if "Queue Size" in self._metrics
            else 0
        )

    def get_current_error_rate(self) -> float:
        """Get the current error rate.

        Returns:
            float: Error rate as a percentage, or 0.0 if not available.
        """
        return (
            self._metrics.get("Error Rate", [0.0])[-1]
            if "Error Rate" in self._metrics
            else 0.0
        )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of key performance metrics.

        Returns:
            Dict[str, Any]: Dictionary with key performance metrics.
        """
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        return {
            "cpu_usage": cpu_usage if cpu_usage is not None else 0.0,
            "memory_usage_mb": memory_usage if memory_usage else 0.0,
            "response_time": self.get_latest_response_time(),
            "operations_per_second": self.get_current_operations_per_second(),
            "active_agents": self.get_active_agents_count(),
            "queue_size": self.get_current_queue_size(),
            "error_rate": self.get_current_error_rate(),
        }

    def get_uptime(self) -> float:
        """Get application uptime in seconds.

        Returns:
            float: Uptime in seconds.
        """
        return time.time() - self.start_time

    def get_metrics_summary(self) -> Dict[str, Dict[str, float]]:
        """Get a summary of all recorded metrics.

        Returns:
            Dict[str, Dict[str, float]]: Summary of metrics with min, max, and average values.
        """
        summary = {}
        for metric_name, values in self._metrics.items():
            if values:
                summary[metric_name] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "count": len(values),
                }
        return summary

    def _log_performance_report(self):
        """Log a detailed performance report with current metrics."""
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()

        report_lines = ["Performance Report:"]
        if cpu_usage is not None:
            report_lines.append(f"  CPU Usage: {cpu_usage:.1f}%")
        else:
            report_lines.append("  CPU Usage: unavailable")

        if memory_usage:
            report_lines.append(f"  Memory Usage (RSS): {memory_usage:.1f} MB")
        else:
            report_lines.append("  Memory Usage: unavailable")

        for metric_name, values in self._metrics.items():
            if values:
                avg = sum(values) / len(values)
                report_lines.append(f"  Metric - {metric_name}: Average = {avg:.2f}")

        logger.info("\n".join(report_lines))

    def log_performance_report(self, interval: int = 1800) -> None:
        """Log a detailed performance report.

        Args:
            interval (int): Time interval in seconds between reports.
            Defaults to 1800 (30 minutes).
        """
        self._log_performance_report()
        logger.info(f"Next performance report in {interval} seconds")
