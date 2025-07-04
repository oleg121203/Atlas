"""
Performance monitoring module for Atlas application.

This module provides comprehensive monitoring of system performance metrics including CPU usage,
memory consumption, response times, operations per second, active agents, queue size, and error rates.
It integrates with the UI to display real-time performance data and supports optimization efforts.
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors and collects performance metrics across the application.

    This class provides methods to track CPU usage, memory consumption,
    response times, operation rates, and other performance metrics crucial
    for maintaining optimal application performance.
    """

    def __init__(self, sampling_interval: float = 1.0, enable_ui_tracking: bool = True):
        """Initialize the performance monitor.

        Args:
            sampling_interval: Time between metric samples in seconds
            enable_ui_tracking: Whether to track UI responsiveness metrics
        """
        self.sampling_interval = sampling_interval
        self.enable_ui_tracking = enable_ui_tracking
        self.running = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # Performance metrics storage
        self.metrics: Dict[str, List[float]] = {
            "cpu_usage": [],
            "memory_usage": [],
            "response_time": [],
            "operations_per_second": [],
            "active_agents": [],
            "queue_size": [],
            "error_rate": [],
        }

        # Operation timings for latency tracking
        self.operation_timings: Dict[str, List[float]] = {}

        logger.info("Performance monitor initialized")

    def start(self):
        """Start the performance monitoring thread."""
        if self.running:
            logger.warning("Performance monitor already running")
            return

        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True, name="PerformanceMonitorThread"
        )
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")

    def stop(self):
        """Stop the performance monitoring thread."""
        if not self.running:
            logger.warning("Performance monitor not running")
            return

        self.running = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)
        logger.info("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop that collects metrics at regular intervals."""
        while self.running:
            try:
                # Collect system metrics
                self._collect_system_metrics()

                # Sleep for the sampling interval
                time.sleep(self.sampling_interval)
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                # Continue monitoring despite errors

    def _collect_system_metrics(self):
        """Collect system-level performance metrics."""
        # CPU usage (per core and overall)
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.metrics["cpu_usage"].append(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.metrics["memory_usage"].append(memory_percent)

            # Limit metric history to avoid memory growth
            self._trim_metrics_history(1000)  # Keep last 1000 samples
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def track_operation(self, operation_name: str, start_time: float, end_time: float):
        """Track the execution time of a specific operation.

        Args:
            operation_name: Identifier for the operation being tracked
            start_time: Operation start timestamp
            end_time: Operation end timestamp
        """
        duration = end_time - start_time

        if operation_name not in self.operation_timings:
            self.operation_timings[operation_name] = []

        self.operation_timings[operation_name].append(duration)

        # Limit history to avoid memory growth
        if len(self.operation_timings[operation_name]) > 1000:
            self.operation_timings[operation_name] = self.operation_timings[
                operation_name
            ][-1000:]

    def get_average_latency(self, operation_name: str) -> float:
        """Get the average latency for a specific operation.

        Args:
            operation_name: The operation to get metrics for

        Returns:
            Average latency in seconds, or 0 if no data available
        """
        if (
            operation_name not in self.operation_timings
            or not self.operation_timings[operation_name]
        ):
            return 0.0

        return sum(self.operation_timings[operation_name]) / len(
            self.operation_timings[operation_name]
        )

    def get_metrics_summary(self) -> Dict[str, float]:
        """Get a summary of current performance metrics.

        Returns:
            Dictionary containing average values of all tracked metrics
        """
        summary = {}

        # Calculate averages for all metrics
        for metric_name, values in self.metrics.items():
            if values:
                summary[f"avg_{metric_name}"] = sum(values) / len(values)
                summary[f"max_{metric_name}"] = max(values)
            else:
                summary[f"avg_{metric_name}"] = 0.0
                summary[f"max_{metric_name}"] = 0.0

        # Add operation latencies
        for op_name, timings in self.operation_timings.items():
            if timings:
                summary[f"latency_{op_name}"] = sum(timings) / len(timings)
            else:
                summary[f"latency_{op_name}"] = 0.0

        return summary

    def _trim_metrics_history(self, max_samples: int):
        """Trim metric history to avoid unbounded memory growth.

        Args:
            max_samples: Maximum number of samples to keep per metric
        """
        for metric_name in self.metrics:
            if len(self.metrics[metric_name]) > max_samples:
                self.metrics[metric_name] = self.metrics[metric_name][-max_samples:]

    def reset_metrics(self):
        """Reset all collected metrics."""
        for metric_name in self.metrics:
            self.metrics[metric_name] = []

        for op_name in self.operation_timings:
            self.operation_timings[op_name] = []

        logger.info("Performance metrics reset")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of key performance metrics.

        Returns:
            Dict containing key performance indicators
        """

        # Get the most recent metrics if available
        cpu_usage = self.metrics["cpu_usage"][-1] if self.metrics["cpu_usage"] else 0.0
        memory_usage = (
            self.metrics["memory_usage"][-1] if self.metrics["memory_usage"] else 0.0
        )
        response_time = (
            self.metrics["response_time"][-1] if self.metrics["response_time"] else 0.0
        )
        ops_per_sec = (
            self.metrics["operations_per_second"][-1]
            if self.metrics["operations_per_second"]
            else 0.0
        )
        active_agents = (
            self.metrics["active_agents"][-1] if self.metrics["active_agents"] else 0
        )
        queue_size = self.metrics["queue_size"][-1] if self.metrics["queue_size"] else 0
        error_rate = (
            self.metrics["error_rate"][-1] if self.metrics["error_rate"] else 0.0
        )

        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "response_time": response_time,
            "operations_per_second": ops_per_sec,
            "active_agents": int(active_agents),
            "queue_size": int(queue_size),
            "error_rate": error_rate,
            "uptime": time.time() - self.start_time
            if hasattr(self, "start_time")
            else 0.0,
        }


# Singleton instance for global access
_instance = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance.

    Returns:
        Singleton instance of PerformanceMonitor
    """
    global _instance
    if _instance is None:
        _instance = PerformanceMonitor()
    return _instance


def track_operation_performance(operation_name: str, func_to_track=None):
    """Helper decorator for tracking operation performance.

    This is a convenience function that can be used as a decorator to track
    the performance of any function in the Atlas application.

    Args:
        operation_name: Name of the operation to track
        func_to_track: Function to track (automatically provided when used as decorator)

    Returns:
        Decorated function that tracks performance

    Example:
        @track_operation_performance("ui_rendering")
        def render_ui_component():
            # Function implementation
    """
    import functools

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                end_time = time.time()
                monitor.track_operation(operation_name, start_time, end_time)

        return wrapper

    # Handle case when used as function or decorator
    if func_to_track is None:
        return decorator
    else:
        return decorator(func_to_track)
