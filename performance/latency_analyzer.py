"""
Latency Analyzer for Atlas

This module provides tools for analyzing latency and identifying bottlenecks within Atlas.
"""

import logging
import statistics
import time
from typing import Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)


class LatencyAnalyzer:
    """Class for analyzing latency in Atlas operations."""

    def __init__(self):
        """Initialize the LatencyAnalyzer."""
        self._operation_times: Dict[str, List[float]] = {}
        self._start_times: Dict[str, float] = {}
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
            latency = (end_time - self._start_times[operation_name]) * 1000  # Convert to milliseconds
            if operation_name not in self._operation_times:
                self._operation_times[operation_name] = []
            self._operation_times[operation_name].append(latency)
            del self._start_times[operation_name]
            logger.debug(f"Ended timing operation: {operation_name}, Latency: {latency:.2f}ms")
            return latency
        else:
            logger.warning(f"Operation not started: {operation_name}")
            return None

    def get_latency_stats(self, operation_name: str) -> Optional[Dict[str, float]]:
        """Get latency statistics for a specific operation.

        Args:
            operation_name (str): The name of the operation to get stats for.

        Returns:
            Optional[Dict[str, float]]: Dictionary with min, max, avg, and count of latencies if available, None otherwise.
        """
        if operation_name in self._operation_times and self._operation_times[operation_name]:
            latencies = self._operation_times[operation_name]
            return {
                "min": min(latencies),
                "max": max(latencies),
                "average": sum(latencies) / len(latencies),
                "median": statistics.median(latencies),
                "count": len(latencies),
                "exceeds_threshold": sum(latencies) / len(latencies) > 100,
                "threshold": 100
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

    def check_latency_threshold(self, operation_name: str, threshold_ms: float) -> bool:
        """Check if the average latency for an operation exceeds a threshold.

        Args:
            operation_name (str): The name of the operation to check.
            threshold_ms (float): The latency threshold in milliseconds.

        Returns:
            bool: True if average latency exceeds threshold, False otherwise.
        """
        stats = self.get_latency_stats(operation_name)
        if stats and stats["average"] > threshold_ms:
            logger.warning(f"Latency threshold exceeded for {operation_name}: {stats['average']:.2f}ms > {threshold_ms}ms")
            return True
        return False

    def suggest_optimizations(self, operation_name: str) -> List[str]:
        """Suggest optimizations for operations with high latency.

        Args:
            operation_name (str): The name of the operation to analyze.

        Returns:
            List[str]: List of optimization suggestions.
        """
        suggestions = []
        stats = self.get_latency_stats(operation_name)
        if stats:
            if stats["average"] > 100:
                suggestions.append(f"Optimize {operation_name} - high average latency ({stats['average']:.2f}ms)")
                if stats["max"] > stats["average"] * 1.5:
                    suggestions.append("Investigate occasional spikes in latency")
                if stats["count"] > 100:
                    suggestions.append("Consider caching frequent operations")
                if 'screen' in operation_name.lower() or 'input' in operation_name.lower():
                    suggestions.append("Target latency <100ms for user interaction")
                elif 'planning' in operation_name.lower():
                    suggestions.append("Target latency <500ms for planning operations")
                elif 'memory' in operation_name.lower():
                    suggestions.append("Target latency <200ms for memory operations")
        if suggestions:
            logger.info(f"Optimization suggestions for {operation_name}: {', '.join(suggestions)}")
        return suggestions

    def log_latency_report(self) -> None:
        """Log a comprehensive latency report for all operations."""
        if not self._operation_times:
            logger.info("No latency data available for report")
            return

        report = ["Latency Report:"]
        for operation, times in self._operation_times.items():
            stats = self.get_latency_stats(operation)
            if stats:
                report.append(f"  Operation: {operation}")
                report.append(f"    Count: {stats['count']}")
                report.append(f"    Average: {stats['average']:.3f} ms")
                report.append(f"    Min: {stats['min']:.3f} ms")
                report.append(f"    Max: {stats['max']:.3f} ms")
                report.append(f"    Median: {stats['median']:.3f} ms")
                if stats['exceeds_threshold']:
                    report.append(f"    WARNING: Latency exceeds threshold of {stats['threshold']:.0f} ms")
                    optimizations = self.suggest_optimizations(operation)
                    if optimizations:
                        report.append("    Suggested Optimizations:")
                        for opt in optimizations:
                            report.append(f"      - {opt}")
        logger.info("\n".join(report))
