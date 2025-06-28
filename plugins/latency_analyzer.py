"""
Advanced Latency Analysis Tools for Atlas

This module provides sophisticated tools for analyzing latency across various components
of the Atlas system. It identifies bottlenecks, suggests optimizations, and integrates with
the performance monitoring dashboard for real-time insights.
"""
import logging
import statistics
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# For UI integration (mocked for now as PySide6 might not be available)
try:
    from PySide6.QtCore import QObject, Signal
    PYSIDE_AVAILABLE = True
except ImportError:
    logger.warning("PySide6 not available. UI integration will be mocked.")
    PYSIDE_AVAILABLE = False
    # Mock QObject and Signal for non-UI testing
    class QObject:
        pass

    class Signal:
        def __init__(self, *args):
            pass

        def emit(self, *args):
            pass


class LatencyAnalyzer(QObject):
    """Analyzes latency data to identify bottlenecks and suggest optimizations for Atlas."""
    # Signals for UI updates
    bottleneck_identified = Signal(dict)
    optimization_suggested = Signal(dict)
    latency_analysis_updated = Signal(dict)

    def __init__(self, atlas_root_path: str, analysis_interval: int = 60):
        """Initialize the Latency Analyzer with the root path of Atlas.

        Args:
            atlas_root_path: The root directory path of the Atlas project.
            analysis_interval: Interval in seconds between latency analyses (default: 1 minute).
        """
        super().__init__()
        self.atlas_root_path = atlas_root_path
        self.analysis_interval = analysis_interval
        self.latency_data: Dict[str, List[float]] = defaultdict(list)
        self.bottleneck_threshold = 0.5  # Threshold for identifying bottlenecks in seconds
        self.dashboard_enabled = PYSIDE_AVAILABLE
        self.is_analyzing = False
        logger.info(f"Latency Analyzer initialized with root path: {atlas_root_path}")

    def add_latency_data(self, operation_name: str, duration: float) -> None:
        """Add latency data for a specific operation.

        Args:
            operation_name: Name of the operation being measured.
            duration: Duration of the operation in seconds.
        """
        try:
            self.latency_data[operation_name].append(duration)
            # Keep only the last 200 measurements to avoid unbounded growth
            if len(self.latency_data[operation_name]) > 200:
                self.latency_data[operation_name] = self.latency_data[operation_name][-200:]
            logger.info(f"Added latency data for {operation_name}: {duration:.3f} seconds")
        except Exception as e:
            logger.error(f"Failed to add latency data for {operation_name}: {e}")

    def analyze_latencies(self) -> Dict[str, dict]:
        """Analyze collected latency data to generate statistics and identify issues.

        Returns:
            Dict[str, dict]: Dictionary of analysis results for each operation.
        """
        try:
            analysis_results = {}
            for operation, durations in self.latency_data.items():
                if not durations:
                    continue
                avg_latency = statistics.mean(durations)
                max_latency = max(durations)
                min_latency = min(durations)
                count = len(durations)
                analysis_results[operation] = {
                    "average": avg_latency,
                    "max": max_latency,
                    "min": min_latency,
                    "count": count,
                    "is_bottleneck": avg_latency > self.bottleneck_threshold
                }
                if analysis_results[operation]["is_bottleneck"]:
                    bottleneck_info = {
                        "operation": operation,
                        "average_latency": avg_latency,
                        "max_latency": max_latency,
                        "count": count
                    }
                    if self.dashboard_enabled:
                        self.bottleneck_identified.emit(bottleneck_info)
                    logger.warning(f"Bottleneck detected in {operation}: Average latency {avg_latency:.3f} sec")

            if self.dashboard_enabled:
                self.latency_analysis_updated.emit(analysis_results)
            return analysis_results
        except Exception as e:
            logger.error(f"Failed to analyze latencies: {e}")
            return {}

    def suggest_optimizations(self, operation: str) -> Optional[Dict[str, str]]:
        """Suggest optimizations for a specific operation based on latency data.

        Args:
            operation: Name of the operation to analyze.

        Returns:
            Optional[Dict[str, str]]: Dictionary with optimization suggestions or None if no data.
        """
        try:
            if operation not in self.latency_data or not self.latency_data[operation]:
                logger.warning(f"No latency data available for {operation}")
                return None

            avg_latency = statistics.mean(self.latency_data[operation])
            if avg_latency > self.bottleneck_threshold:
                suggestion = {
                    "operation": operation,
                    "issue": f"High average latency of {avg_latency:.3f} seconds",
                    "suggestion": "Consider breaking down the operation into smaller tasks or caching results."
                }
                if self.dashboard_enabled:
                    self.optimization_suggested.emit(suggestion)
                logger.info(f"Optimization suggested for {operation}")
                return suggestion
            return None
        except Exception as e:
            logger.error(f"Failed to suggest optimizations for {operation}: {e}")
            return None

    def get_worst_performers(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get the operations with the highest average latencies.

        Args:
            limit: Number of top worst performers to return (default: 5).

        Returns:
            List[Tuple[str, float]]: List of tuples with operation name and average latency.
        """
        try:
            performance_list = []
            for operation, durations in self.latency_data.items():
                if durations:
                    performance_list.append((operation, statistics.mean(durations)))
            # Sort by average latency in descending order
            performance_list.sort(key=lambda x: x[1], reverse=True)
            return performance_list[:limit]
        except Exception as e:
            logger.error(f"Failed to get worst performers: {e}")
            return []

    def set_bottleneck_threshold(self, threshold: float) -> None:
        """Set the threshold for identifying bottlenecks.

        Args:
            threshold: Latency threshold in seconds above which an operation is considered a bottleneck.
        """
        try:
            self.bottleneck_threshold = threshold
            logger.info(f"Bottleneck threshold set to {threshold:.3f} seconds")
        except Exception as e:
            logger.error(f"Failed to set bottleneck threshold: {e}")

    def start_analysis(self) -> bool:
        """Start periodic latency analysis.

        Returns:
            bool: True if analysis started successfully, False otherwise.
        """
        if self.is_analyzing:
            logger.warning("Latency analysis is already running.")
            return False
        try:
            import time
            from threading import Thread

            def analysis_loop():
                while self.is_analyzing:
                    self.analyze_latencies()
                    # Suggest optimizations for worst performers
                    worst_performers = self.get_worst_performers()
                    for operation, _ in worst_performers:
                        self.suggest_optimizations(operation)
                    time.sleep(self.analysis_interval)

            self.is_analyzing = True
            analysis_thread = Thread(target=analysis_loop, daemon=True)
            analysis_thread.start()
            logger.info("Started latency analysis thread.")
            return True
        except Exception as e:
            logger.error(f"Failed to start latency analysis: {e}")
            self.is_analyzing = False
            return False

    def stop_analysis(self) -> bool:
        """Stop periodic latency analysis.

        Returns:
            bool: True if analysis stopped successfully, False otherwise.
        """
        if not self.is_analyzing:
            logger.warning("Latency analysis is not running.")
            return False
        try:
            self.is_analyzing = False
            logger.info("Stopped latency analysis.")
            return True
        except Exception as e:
            logger.error(f"Failed to stop latency analysis: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    import os
    import time

    atlas_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analyzer = LatencyAnalyzer(atlas_root, analysis_interval=10)
    # Simulate some latency data
    analyzer.add_latency_data("Operation1", 0.3)
    analyzer.add_latency_data("Operation1", 0.7)
    analyzer.add_latency_data("Operation2", 1.2)
    analyzer.add_latency_data("Operation2", 1.5)
    # Analyze latencies
    results = analyzer.analyze_latencies()
    logger.info(f"Latency Analysis Results: {results}")
    # Suggest optimizations
    suggestion = analyzer.suggest_optimizations("Operation2")
    if suggestion:
        logger.info(f"Optimization Suggestion: {suggestion}")
    # Get worst performers
    worst = analyzer.get_worst_performers(limit=2)
    logger.info(f"Worst Performers: {worst}")
    # Start periodic analysis
    if analyzer.start_analysis():
        time.sleep(20)  # Let analysis run for a bit
        analyzer.stop_analysis()
