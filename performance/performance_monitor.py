"""
Performance Monitor Module

This module provides performance monitoring for the Atlas application.
"""

import logging
import os
import time
from typing import Any, Dict, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

try:
    import tracemalloc
    TRACEMALLOC_AVAILABLE = True
except ImportError:
    TRACEMALLOC_AVAILABLE = False
    tracemalloc = None

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Class for monitoring performance metrics in Atlas."""

    def __init__(self):
        """Initialize the PerformanceMonitor."""
        self.start_time = time.time()
        self._metrics = {}
        self.process = None  # type: Optional['psutil.Process']
        if psutil is not None:
            try:
                self.process = psutil.Process(os.getpid())
            except Exception as e:
                logger.warning(f"Failed to initialize process monitor: {e}")
        else:
            logger.warning("psutil not available, CPU and memory metrics will be limited")
        if TRACEMALLOC_AVAILABLE:
            self.start_memory_tracing()
        else:
            logger.warning("tracemalloc not available, memory tracing will be disabled")
        logger.info("PerformanceMonitor initialized")

    def record_metric(self, metric_name: str, value: float) -> None:
        """Record a performance metric.

        Args:
            metric_name (str): The name of the metric.
            value (float): The value of the metric.
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        self._metrics[metric_name].append(value)
        logger.debug(f"Metric recorded: {metric_name} = {value}")

    def get_cpu_usage(self) -> Optional[float]:
        """Get current CPU usage percentage for the process.

        Returns:
            Optional[float]: CPU usage percentage if psutil is available, None otherwise.
        """
        if self.process is not None and psutil is not None:
            try:
                return self.process.cpu_percent(interval=1)
            except Exception as e:
                logger.warning(f"Failed to get CPU usage: {e}")
                return None
        logger.warning("psutil not available for CPU usage monitoring")
        return None

    def get_memory_usage(self) -> Optional[Dict[str, float]]:
        """Get current memory usage for the process.

        Returns:
            Optional[Dict[str, float]]: Dictionary with RSS and VMS memory usage in MB
            if psutil is available, None otherwise.
        """
        if self.process is not None and psutil is not None:
            try:
                mem_info = self.process.memory_info()
                return {"rss": mem_info.rss / 1024 / 1024, "vms": mem_info.vms / 1024 / 1024}
            except Exception as e:
                logger.warning(f"Failed to get memory usage: {e}")
                return None
        logger.warning("psutil not available for memory usage monitoring")
        return None

    def start_memory_tracing(self) -> None:
        """Start memory allocation tracing if tracemalloc is available."""
        if not TRACEMALLOC_AVAILABLE or tracemalloc is None:
            logger.warning("tracemalloc not available for memory tracing")
            return
        tracemalloc.start()
        logger.info("Memory allocation tracing started")

    def stop_memory_tracing(self) -> None:
        """Stop memory allocation tracing if tracemalloc is available."""
        if not TRACEMALLOC_AVAILABLE or tracemalloc is None:
            logger.warning("tracemalloc not available for memory tracing")
            return
        tracemalloc.stop()
        logger.info("Memory allocation tracing stopped")

    def get_memory_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get a snapshot of current memory allocations if tracemalloc is available.

        Returns:
            Optional[Dict[str, Any]]: Snapshot data if tracemalloc is available, None otherwise.
        """
        if not TRACEMALLOC_AVAILABLE or tracemalloc is None:
            logger.warning("tracemalloc not available for memory snapshot")
            return None
        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics("lineno")
        return {
            "total_size": sum(stat.size for stat in stats),
            "top_allocations": [
                {
                    "size": stat.size,
                    "count": stat.count,
                    "traceback": str(stat.traceback),
                }
                for stat in stats[:3]
            ],
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
                    "count": len(values)
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
            report_lines.append(f"  Memory Usage (RSS): {memory_usage['rss']:.1f} MB")
            report_lines.append(f"  Memory Usage (VMS): {memory_usage['vms']:.1f} MB")
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
