"""
Latency Analyzer for Atlas

This module provides tools for analyzing latency and identifying bottlenecks within Atlas.
"""

import functools
import logging
import statistics
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for function return type preservation
T = TypeVar("T")


class LatencyAnalyzer:
    """Class for analyzing latency in Atlas operations."""

    def __init__(self):
        """Initialize the LatencyAnalyzer."""
        self._operation_times: Dict[str, List[float]] = {}
        self._start_times: Dict[str, float] = {}
        self.thresholds: Dict[str, float] = {
            "ui_operation": 100.0,  # 100ms threshold for UI operations
            "memory_operation": 50.0,  # 50ms threshold for memory operations
            "plugin_load": 200.0,  # 200ms threshold for plugin loading
            "tool_execution": 150.0,  # 150ms threshold for tool execution
            "default": 200.0,  # 200ms default threshold
        }
        logger.info("LatencyAnalyzer initialized")

    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation.

        Args:
            operation_name (str): The name of the operation to start timing.
        """
        self._start_times[operation_name] = time.time()
        logger.debug(f"Started timing operation: {operation_name}")

    def end_operation(self, operation_name: str) -> Optional[float]:
        """End timing an operation and record the latency.

        Args:
            operation_name (str): The name of the operation to end timing.

        Returns:
            Optional[float]: The latency of the operation in milliseconds if started, None otherwise.
        """
        if operation_name in self._start_times:
            end_time = time.time()
            latency = (
                end_time - self._start_times[operation_name]
            ) * 1000  # Convert to milliseconds
            if operation_name not in self._operation_times:
                self._operation_times[operation_name] = []
            self._operation_times[operation_name].append(latency)
            del self._start_times[operation_name]
            logger.debug(
                f"Ended timing operation: {operation_name}, Latency: {latency:.2f}ms"
            )
            return latency
        else:
            logger.warning(f"Operation not started: {operation_name}")
            return None

    def get_latency_stats(self, operation_name: str) -> Optional[Dict[str, float]]:
        """Get latency statistics for a specific operation.

        Args:
            operation_name (str): The name of the operation to get stats for.

        Returns:
            Optional[Dict[str, float]]: Dictionary containing latency statistics,
                or None if operation not found.
        """
        if (
            operation_name in self._operation_times
            and self._operation_times[operation_name]
        ):
            latencies = self._operation_times[operation_name]
            threshold = self.thresholds.get(operation_name, self.thresholds["default"])
            return {
                "min": min(latencies),
                "max": max(latencies),
                "average": sum(latencies) / len(latencies),
                "median": statistics.median(latencies),
                "count": len(latencies),
                "exceeds_threshold": sum(latencies) / len(latencies) > threshold,
                "threshold": threshold,
            }
        return None

    def get_all_latency_stats(self) -> Dict[str, Dict[str, float]]:
        """Get latency statistics for all operations.

        Returns:
            Dict[str, Dict[str, float]]: Dictionary of operation names to their latency stats.
        """
        stats = {}
        for operation_name in self._operation_times:
            operation_stats = self.get_latency_stats(operation_name)
            if operation_stats:
                stats[operation_name] = operation_stats
        return stats

    def measure(
        self, operation_name: str
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator to measure the latency of a function.

        Args:
            operation_name (str): The name of the operation being measured.

        Returns:
            Callable: Decorator function that adds latency measurement.
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                self.start_operation(operation_name)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    self.end_operation(operation_name)

            return wrapper

        return decorator

    def reset_stats(self) -> None:
        """Reset all recorded latency statistics."""
        self._operation_times.clear()
        self._start_times.clear()
        logger.info("Latency statistics reset")

    def export_stats(self) -> Dict[str, Any]:
        """Export all latency statistics for external analysis.

        Returns:
            Dict[str, Any]: Complete statistics data structure.
        """
        return {
            "operation_times": dict(self._operation_times),
            "statistics": self.get_all_latency_stats(),
            "thresholds": dict(self.thresholds),
        }


# Global instance
_latency_analyzer = None


def get_latency_analyzer() -> LatencyAnalyzer:
    """Get the global latency analyzer instance.

    Returns:
        LatencyAnalyzer: The global latency analyzer instance.
    """
    global _latency_analyzer
    if _latency_analyzer is None:
        _latency_analyzer = LatencyAnalyzer()
    return _latency_analyzer


def measure_latency(
    operation_type: str,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for measuring function latency.

    Args:
        operation_type: The type of operation being measured

    Returns:
        Decorator function that adds latency measurement
    """
    analyzer = get_latency_analyzer()
    return analyzer.measure(operation_type)
