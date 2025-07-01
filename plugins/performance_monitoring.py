"""
Performance Monitoring Utilities for Atlas

This module provides utilities for monitoring system performance, including CPU and memory usage,
tracking memory allocations, measuring latency of operations, and generating performance reports.

Enhanced with real-time dashboard integration in the Atlas UI to visualize performance metrics
dynamically and provide actionable insights for optimization.
"""

import logging
import os
import time
import tracemalloc
from threading import Thread
from typing import Dict, List, Optional

import psutil

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


class PerformanceMonitor(QObject):
    """Monitors system performance metrics and integrates with UI for real-time dashboard display."""

    # Signals for UI updates
    cpu_usage_updated = Signal(float)
    memory_usage_updated = Signal(float)
    latency_updated = Signal(dict)
    performance_report_ready = Signal(str)

    def __init__(self, atlas_root_path: str, report_interval: int = 300):
        """Initialize the Performance Monitor with the root path of Atlas.

        Args:
            atlas_root_path: The root directory path of the Atlas project.
            report_interval: Interval in seconds between performance reports (default: 5 minutes).
        """
        super().__init__()
        self.atlas_root_path = atlas_root_path
        self.report_path = os.path.join(atlas_root_path, "logs", "performance_reports")
        self.report_interval = report_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[Thread] = None
        self.process = psutil.Process()
        self.latency_data: Dict[str, List[float]] = {}
        self.dashboard_enabled = PYSIDE_AVAILABLE
        logger.info(
            f"Performance Monitor initialized with root path: {atlas_root_path}"
        )

    def start_monitoring(self) -> bool:
        """Start continuous performance monitoring in a separate thread.

        Returns:
            bool: True if monitoring started successfully, False otherwise.
        """
        if self.is_monitoring:
            logger.warning("Performance monitoring is already running.")
            return False

        try:
            # Create logs directory if it doesn't exist
            os.makedirs(self.report_path, exist_ok=True)

            # Start tracemalloc for memory allocation tracking
            tracemalloc.start()

            # Start monitoring thread
            self.is_monitoring = True
            self.monitor_thread = Thread(target=self._monitor_performance, daemon=True)
            self.monitor_thread.start()

            # Initialize dashboard (mocked if PySide6 is not available)
            if self.dashboard_enabled:
                logger.info("Performance dashboard integration enabled.")
            else:
                logger.warning(
                    "Performance dashboard integration mocked due to missing PySide6."
                )

            return True
        except Exception as e:
            logger.error(f"Failed to start performance monitoring: {e}")
            self.is_monitoring = False
            return False

    def stop_monitoring(self) -> bool:
        """Stop performance monitoring.

        Returns:
            bool: True if monitoring stopped successfully, False otherwise.
        """
        if not self.is_monitoring:
            logger.warning("Performance monitoring is not running.")
            return False

        try:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2.0)
                if self.monitor_thread.is_alive():
                    logger.warning(
                        "Performance monitoring thread did not terminate gracefully."
                    )
                else:
                    logger.info("Performance monitoring thread terminated.")
            tracemalloc.stop()
            return True
        except Exception as e:
            logger.error(f"Failed to stop performance monitoring: {e}")
            return False

    def _monitor_performance(self):
        """Continuously monitor performance metrics and update dashboard."""
        last_report_time = time.time()

        while self.is_monitoring:
            try:
                # Collect CPU and memory usage
                cpu_usage = self.get_cpu_usage()
                memory_usage = self.get_memory_usage()

                # Emit signals for dashboard updates
                if self.dashboard_enabled:
                    self.cpu_usage_updated.emit(cpu_usage)
                    self.memory_usage_updated.emit(memory_usage)
                else:
                    logger.info(
                        f"CPU Usage: {cpu_usage:.1f}% | Memory Usage: {memory_usage:.1f}%"
                    )

                # Check if it's time to generate a report
                current_time = time.time()
                if current_time - last_report_time >= self.report_interval:
                    report_content = self.generate_performance_report()
                    if self.dashboard_enabled:
                        self.performance_report_ready.emit(report_content)
                    last_report_time = current_time

                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                time.sleep(10)  # Wait longer if there's an error

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage for the Atlas process.

        Returns:
            float: CPU usage percentage.
        """
        try:
            cpu_usage = self.process.cpu_percent(interval=1)
            return cpu_usage
        except Exception as e:
            logger.error(f"Failed to get CPU usage: {e}")
            return 0.0

    def get_memory_usage(self) -> float:
        """Get current memory usage percentage for the Atlas process.

        Returns:
            float: Memory usage percentage.
        """
        try:
            memory_info = self.process.memory_percent()
            return memory_info
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0.0

    def track_memory_allocations(self, limit: int = 10) -> List[str]:
        """Track memory allocations and return top allocations.

        Args:
            limit: Number of top allocations to return (default: 10).

        Returns:
            List[str]: List of strings describing the top memory allocations.
        """
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")
            result = [f"[Top {limit} Memory Allocations]"]
            for stat in top_stats[:limit]:
                result.append(str(stat))
            return result
        except Exception as e:
            logger.error(f"Failed to track memory allocations: {e}")
            return ["Error tracking memory allocations."]

    def measure_latency(self, operation_name: str, duration: float) -> None:
        """Record the latency of a specific operation.

        Args:
            operation_name: Name of the operation being measured.
            duration: Duration of the operation in seconds.
        """
        try:
            if operation_name not in self.latency_data:
                self.latency_data[operation_name] = []
            self.latency_data[operation_name].append(duration)

            # Keep only the last 100 measurements to avoid unbounded growth
            if len(self.latency_data[operation_name]) > 100:
                self.latency_data[operation_name] = self.latency_data[operation_name][
                    -100:
                ]

            # Emit signal for dashboard update
            if self.dashboard_enabled:
                latency_summary = {
                    "operation": operation_name,
                    "latest": duration,
                    "average": sum(self.latency_data[operation_name])
                    / len(self.latency_data[operation_name]),
                }
                self.latency_updated.emit(latency_summary)
            else:
                logger.info(f"Latency for {operation_name}: {duration:.3f} seconds")
        except Exception as e:
            logger.error(f"Failed to measure latency for {operation_name}: {e}")

    def generate_performance_report(self) -> str:
        """Generate a detailed performance report and save it to a file.

        Returns:
            str: Content of the performance report.
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_filename = f"performance_report_{timestamp}.txt"
            report_full_path = os.path.join(self.report_path, report_filename)

            # Collect current metrics
            cpu_usage = self.get_cpu_usage()
            memory_usage = self.get_memory_usage()
            memory_allocations = self.track_memory_allocations()

            # Build report content
            report_content = f"Atlas Performance Report - {timestamp}\n"
            report_content += "=" * 50 + "\n\n"
            report_content += f"CPU Usage: {cpu_usage:.1f}%\n"
            report_content += f"Memory Usage: {memory_usage:.1f}%\n"
            report_content += "\nLatency Statistics:\n"
            for op_name, durations in self.latency_data.items():
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    max_duration = max(durations)
                    min_duration = min(durations)
                    report_content += (
                        f"  - {op_name}:\n"
                        f"    Average: {avg_duration:.3f} sec\n"
                        f"    Max: {max_duration:.3f} sec\n"
                        f"    Min: {min_duration:.3f} sec\n"
                        f"    Count: {len(durations)}\n"
                    )
                else:
                    report_content += f"  - {op_name}: No data available\n"
            report_content += "\nMemory Allocation Details:\n"
            report_content += "\n".join(memory_allocations) + "\n"

            # Save report to file
            with open(report_full_path, "w", encoding="utf-8") as f:
                f.write(report_content)

            logger.info(f"Generated performance report: {report_full_path}")
            return report_content
        except Exception as e:
            error_msg = f"Failed to generate performance report: {e}"
            logger.error(error_msg)
            return error_msg

    def get_performance_summary(self) -> Dict[str, float]:
        """Get a summary of current performance metrics for quick reference or UI display.

        Returns:
            Dict[str, float]: Dictionary containing CPU usage, memory usage, and average latencies.
        """
        try:
            summary = {
                "cpu_usage": self.get_cpu_usage(),
                "memory_usage": self.get_memory_usage(),
            }

            # Add average latency for each operation
            for op_name, durations in self.latency_data.items():
                if durations:
                    summary[f"{op_name}_avg_latency"] = sum(durations) / len(durations)

            return summary
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {"error": 0.0}

    def setup_dashboard_ui(self) -> bool:
        """Setup the performance dashboard UI components (mocked if PySide6 is unavailable).

        Returns:
            bool: True if dashboard setup is successful or mocked, False otherwise.
        """
        if not self.dashboard_enabled:
            logger.warning("Dashboard UI setup skipped: PySide6 not available.")
            return True  # Mocked success

        try:
            # In a real implementation, this would create UI widgets for displaying metrics
            logger.info("Setting up performance dashboard UI components.")
            # Placeholder for actual UI setup code
            return True
        except Exception as e:
            logger.error(f"Failed to setup performance dashboard UI: {e}")
            return False

    def update_dashboard(self) -> bool:
        """Update the performance dashboard with the latest metrics (mocked if PySide6 is unavailable).

        Returns:
            bool: True if dashboard update is successful or mocked, False otherwise.
        """
        if not self.dashboard_enabled:
            logger.info("Dashboard update mocked: PySide6 not available.")
            return True  # Mocked success

        try:
            # In a real implementation, this would update UI elements with new data
            cpu_usage = self.get_cpu_usage()
            memory_usage = self.get_memory_usage()
            self.cpu_usage_updated.emit(cpu_usage)
            self.memory_usage_updated.emit(memory_usage)
            logger.info("Updated performance dashboard with latest metrics.")
            return True
        except Exception as e:
            logger.error(f"Failed to update performance dashboard: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    atlas_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    monitor = PerformanceMonitor(atlas_root, report_interval=30)
    if monitor.start_monitoring():
        # Simulate some operations with latency
        start_time = time.time()
        time.sleep(1)  # Simulate work
        monitor.measure_latency("MockOperation", time.time() - start_time)

        # Setup and update dashboard
        monitor.setup_dashboard_ui()
        monitor.update_dashboard()

        # Generate an immediate report for testing
        report = monitor.generate_performance_report()
        logger.info(f"Immediate Report:\n{report}")

        time.sleep(10)  # Let monitoring run for a bit
        monitor.stop_monitoring()
