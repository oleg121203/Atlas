"""
Custom Latency Logger for Atlas

This module implements a custom latency logger that monitors and logs latency for various operations
in Atlas, auto-generating performance reports every 30 minutes to ensure performance thresholds are met.
"""
import logging
import os
import threading
import time
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class LatencyLogger:
    """Manages latency logging for Atlas, auto-generating performance reports periodically."""

    REPORT_INTERVAL_SECONDS = 1800  # 30 minutes

    def __init__(self, atlas_root_path: str):
        """Initialize the latency logger with the root path of Atlas.

        Args:
            atlas_root_path: The root directory path of the Atlas project.
        """
        self.atlas_root_path = atlas_root_path
        self.latency_log_path = os.path.join(atlas_root_path, "logs", "latency.log")
        self.is_initialized = False
        self.is_running = False
        self.latency_data: Dict[str, list] = {}
        self.report_thread: Optional[threading.Thread] = None
        logger.info(f"Latency Logger initialized with root path: {atlas_root_path}")

    def initialize(self) -> bool:
        """Initialize the latency logger by setting up logging directories.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(self.latency_log_path), exist_ok=True)

            self.is_initialized = True
            logger.info("Latency Logger for Atlas initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Latency Logger: {e}")
            return False

    def start_auto_reporting(self) -> bool:
        """Start the auto-reporting thread to generate performance reports every 30 minutes.

        Returns:
            bool: True if auto-reporting started successfully, False otherwise.
        """
        if not self.is_initialized:
            logger.error("Latency Logger not initialized. Call initialize() first.")
            return False

        if self.is_running:
            logger.warning("Auto-reporting is already running.")
            return True

        try:
            self.is_running = True
            self.report_thread = threading.Thread(target=self._generate_reports_periodically)
            self.report_thread.daemon = True
            self.report_thread.start()
            logger.info("Started auto-reporting for latency performance every 30 minutes.")
            return True
        except Exception as e:
            logger.error(f"Failed to start auto-reporting: {e}")
            self.is_running = False
            return False

    def stop_auto_reporting(self) -> bool:
        """Stop the auto-reporting thread.

        Returns:
            bool: True if auto-reporting stopped successfully, False otherwise.
        """
        if not self.is_initialized:
            logger.error("Latency Logger not initialized. Call initialize() first.")
            return False

        if not self.is_running:
            logger.warning("Auto-reporting is not running.")
            return True

        try:
            self.is_running = False
            if self.report_thread:
                self.report_thread.join(timeout=2.0)
                if self.report_thread.is_alive():
                    logger.warning("Auto-reporting thread did not terminate gracefully.")
                else:
                    logger.info("Auto-reporting thread terminated successfully.")
            self.report_thread = None
            logger.info("Stopped auto-reporting for latency performance.")
            return True
        except Exception as e:
            logger.error(f"Failed to stop auto-reporting: {e}")
            return False

    def _generate_reports_periodically(self):
        """Periodically generate performance reports based on latency logs."""
        while self.is_running:
            try:
                time.sleep(self.REPORT_INTERVAL_SECONDS)
                if not self.is_running:
                    break
                self.generate_performance_report()
            except Exception as e:
                logger.error(f"Error in periodic report generation: {e}")

    def log_latency(self, operation_name: str, latency_ms: float) -> bool:
        """Log latency for a specific operation.

        Args:
            operation_name: Name of the operation.
            latency_ms: Latency in milliseconds.

        Returns:
            bool: True if logging is successful, False otherwise.
        """
        if not self.is_initialized:
            logger.error("Latency Logger not initialized. Call initialize() first.")
            return False

        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {operation_name}: {latency_ms:.2f} ms\n"

            with open(self.latency_log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)

            # Store in memory for quick access in reports
            if operation_name not in self.latency_data:
                self.latency_data[operation_name] = []
            self.latency_data[operation_name].append({
                "timestamp": timestamp,
                "latency_ms": latency_ms
            })

            # Limit to last 100 entries per operation to manage memory usage
            if len(self.latency_data[operation_name]) > 100:
                self.latency_data[operation_name] = self.latency_data[operation_name][-100:]

            logger.debug(f"Logged latency for {operation_name}: {latency_ms:.2f} ms")
            return True
        except Exception as e:
            logger.error(f"Failed to log latency for {operation_name}: {e}")
            return False

    def get_latency_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve latency statistics for a specific operation or all operations.

        Args:
            operation_name: Optional name of the operation to get stats for. If None, stats for
                            all operations are returned.

        Returns:
            Dict[str, Any]: Dictionary with latency statistics.
        """
        if not self.is_initialized:
            logger.error("Latency Logger not initialized. Call initialize() first.")
            return {"error": "Not initialized"}

        try:
            if operation_name:
                if operation_name in self.latency_data:
                    latencies = [entry["latency_ms"] for entry in self.latency_data[operation_name]]
                    if latencies:
                        return {
                            "operation": operation_name,
                            "count": len(latencies),
                            "average_ms": sum(latencies) / len(latencies),
                            "min_ms": min(latencies),
                            "max_ms": max(latencies),
                            "last_10_entries": self.latency_data[operation_name][-10:]
                        }
                    return {
                        "operation": operation_name,
                        "count": 0,
                        "average_ms": 0.0,
                        "min_ms": 0.0,
                        "max_ms": 0.0,
                        "last_10_entries": []
                    }
                return {
                    "operation": operation_name,
                    "error": "Operation not found"
                }
            else:
                stats = {}
                for op, data in self.latency_data.items():
                    latencies = [entry["latency_ms"] for entry in data]
                    if latencies:
                        stats[op] = {
                            "count": len(latencies),
                            "average_ms": sum(latencies) / len(latencies),
                            "min_ms": min(latencies),
                            "max_ms": max(latencies),
                            "last_10_entries": data[-10:]
                        }
                    else:
                        stats[op] = {
                            "count": 0,
                            "average_ms": 0.0,
                            "min_ms": 0.0,
                            "max_ms": 0.0,
                            "last_10_entries": []
                        }
                return stats
        except Exception as e:
            logger.error(f"Failed to retrieve latency stats: {e}")
            return {"error": str(e)}

    def generate_performance_report(self) -> bool:
        """Generate a performance report based on current latency data.

        Returns:
            bool: True if report generation is successful, False otherwise.
        """
        if not self.is_initialized:
            logger.error("Latency Logger not initialized. Call initialize() first.")
            return False

        try:
            report_path = os.path.join(
                self.atlas_root_path,
                "reports",
                f"latency_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            )
            os.makedirs(os.path.dirname(report_path), exist_ok=True)

            with open(report_path, "w", encoding="utf-8") as f:
                f.write("===== Atlas Latency Performance Report =====\n")
                f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                stats = self.get_latency_stats()
                if "error" in stats:
                    f.write(f"Error retrieving stats: {stats['error']}\n")
                else:
                    for operation, data in stats.items():
                        f.write(f"Operation: {operation}\n")
                        f.write(f"  Count: {data['count']}\n")
                        if data['count'] > 0:
                            f.write(f"  Average Latency: {data['average_ms']:.2f} ms\n")
                            f.write(f"  Minimum Latency: {data['min_ms']:.2f} ms\n")
                            f.write(f"  Maximum Latency: {data['max_ms']:.2f} ms\n")
                        f.write("\n")

            logger.info(f"Latency performance report generated at {report_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate latency performance report: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    atlas_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    latency_logger = LatencyLogger(atlas_root)
    if latency_logger.initialize():
        latency_logger.start_auto_reporting()

        # Simulate logging latency for operations
        latency_logger.log_latency("screen_input", 85.5)
        latency_logger.log_latency("screen_input", 92.3)
        latency_logger.log_latency("planning_operation", 450.7)
        latency_logger.log_latency("memory_operation", 180.2)

        # Retrieve and display stats
        stats = latency_logger.get_latency_stats("screen_input")
        if "error" not in stats:
            logger.info(f"Stats for screen_input: {stats}")

        # Generate a report immediately for testing
        latency_logger.generate_performance_report()

        # Stop auto-reporting after a short delay for testing
        time.sleep(5)
        latency_logger.stop_auto_reporting()
