"""
Performance Audit Script for Atlas

This script conducts a comprehensive performance audit of the Atlas application,
identifying bottlenecks and areas for optimization.
"""

import argparse
import cProfile
import json
import logging
import pstats
import subprocess
import sys
import time
import tracemalloc
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional

import psutil

from core.config import load_config
from core.logging import get_logger

# Set up logging
logger = get_logger("AtlasPerformanceAudit")


class PerformanceAuditError(Exception):
    """Custom exception for performance audit errors."""

    pass


class AtlasPerformanceAuditor:
    """Handles the performance audit of the Atlas application."""

    def __init__(self, environment: str, config_path: Optional[str] = None):
        """
        Initialize the performance auditor with target environment and configuration.

        Args:
            environment: Target environment for audit (dev, staging, prod)
            config_path: Path to configuration file, if any
        """
        self.environment = environment.lower()
        self.config = load_config(config_path, environment=self.environment)
        self.app_name = self.config.get("app_name", "atlas")
        self.audit_dir = Path(self.config.get("audit_dir", "performance_audit"))
        self.report_file = (
            self.audit_dir
            / f"{self.app_name}_performance_report_{self.environment}.json"
        )
        self.setup_logging()
        logger.info(
            "Initialized AtlasPerformanceAuditor for environment: %s", self.environment
        )

    def setup_logging(self) -> None:
        """Set up logging configuration for performance audit."""
        log_level = self.config.get("logging", {}).get("level", "INFO")
        log_file = self.config.get("logging", {}).get(
            "file", f"{self.app_name}_audit.log"
        )
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )
        logger.info("Logging configured for performance audit")

    def check_prerequisites(self) -> bool:
        """
        Check if all prerequisites for performance audit are met.

        Returns:
            bool: True if prerequisites are met, False otherwise
        """
        logger.info("Checking performance audit prerequisites")

        # Check if required tools are installed
        required_tools = ["python", "pip"]
        for tool in required_tools:
            try:
                subprocess.run(
                    [tool, "--version"], check=True, capture_output=True, text=True
                )
                logger.debug("Tool %s is installed", tool)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("Required tool %s is not installed or not found", tool)
                return False

        # Ensure audit directory exists
        self.audit_dir.mkdir(parents=True, exist_ok=True)

        logger.info("All performance audit prerequisites met")
        return True

    def run_benchmarks(self) -> Dict:
        """
        Run predefined benchmarks on the Atlas application.

        Returns:
            Dict: Benchmark results
        """
        logger.info("Running performance benchmarks for Atlas")
        benchmarks = {
            "startup_time": self.measure_startup_time,
            "memory_usage": self.measure_memory_usage,
            "cpu_usage": self.measure_cpu_usage,
            "module_load_time": self.measure_module_load_time,
            "ui_response_time": self.measure_ui_response_time,
        }

        results = {}
        for benchmark_name, benchmark_func in benchmarks.items():
            try:
                logger.info("Executing benchmark: %s", benchmark_name)
                result = benchmark_func()
                results[benchmark_name] = result
                logger.info(
                    "Benchmark %s completed with result: %s", benchmark_name, result
                )
            except Exception as e:
                logger.error(
                    "Error during benchmark %s: %s",
                    benchmark_name,
                    str(e),
                    exc_info=True,
                )
                results[benchmark_name] = {"error": str(e)}

        return results

    def measure_startup_time(self) -> Dict:
        """
        Measure the startup time of the Atlas application.

        Returns:
            Dict: Startup time in seconds
        """
        logger.info("Measuring startup time")
        start_time = time.time()
        try:
            # Replace with actual command to start Atlas
            subprocess.run(
                ["python", "-m", self.app_name],
                timeout=30,
                check=False,
                capture_output=True,
                text=True,
            )
            end_time = time.time()
            startup_duration = end_time - start_time
            return {"duration_seconds": startup_duration}
        except subprocess.TimeoutExpired:
            logger.error("Startup time measurement timed out")
            return {"error": "Timeout during startup", "duration_seconds": -1}
        except Exception as e:
            logger.error("Error measuring startup time: %s", str(e))
            return {"error": str(e), "duration_seconds": -1}

    def measure_memory_usage(self) -> Dict:
        """
        Measure the memory usage of the Atlas application.

        Returns:
            Dict: Memory usage statistics
        """
        logger.info("Measuring memory usage")
        try:
            # Start memory tracing
            tracemalloc.start()

            # Replace with actual Atlas application launch
            process = subprocess.Popen(
                ["python", "-m", self.app_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for a short period to let the app stabilize
            time.sleep(5)

            # Get process info
            ps_process = psutil.Process(process.pid)
            memory_info = ps_process.memory_info()

            # Get memory snapshot from tracemalloc
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")

            # Terminate the process
            process.terminate()
            tracemalloc.stop()

            # Format top memory usage stats
            top_memory_lines = []
            for stat in top_stats[:3]:
                top_memory_lines.append(str(stat))

            return {
                "rss_bytes": memory_info.rss,
                "vms_bytes": memory_info.vms,
                "top_memory_consumers": top_memory_lines,
            }
        except Exception as e:
            logger.error("Error measuring memory usage: %s", str(e), exc_info=True)
            tracemalloc.stop()
            return {"error": str(e)}

    def measure_cpu_usage(self) -> Dict:
        """
        Measure the CPU usage of the Atlas application.

        Returns:
            Dict: CPU usage statistics
        """
        logger.info("Measuring CPU usage")
        try:
            # Replace with actual Atlas application launch
            process = subprocess.Popen(
                ["python", "-m", self.app_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for a short period to let the app stabilize
            time.sleep(5)

            # Get process info
            ps_process = psutil.Process(process.pid)
            cpu_percent = ps_process.cpu_percent(interval=5)

            # Terminate the process
            process.terminate()

            return {"cpu_percent": cpu_percent}
        except Exception as e:
            logger.error("Error measuring CPU usage: %s", str(e), exc_info=True)
            return {"error": str(e)}

    def measure_module_load_time(self) -> Dict:
        """
        Measure the load time of individual modules in Atlas.

        Returns:
            Dict: Module load times
        """
        logger.info("Measuring module load times")
        try:
            module_load_times = {}
            modules_to_test = self.config.get(
                "modules", ["chat", "tasks", "agents", "plugins"]
            )

            for module in modules_to_test:
                start_time = time.time()
                # Replace with actual module loading code
                subprocess.run(
                    ["python", "-c", f"import {self.app_name}.{module}"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                end_time = time.time()
                module_load_times[module] = end_time - start_time

            return module_load_times
        except Exception as e:
            logger.error("Error measuring module load times: %s", str(e), exc_info=True)
            return {"error": str(e)}

    def measure_ui_response_time(self) -> Dict:
        """
        Measure the UI response time for various actions in Atlas.

        Returns:
            Dict: UI response times
        """
        logger.info("Measuring UI response time")
        try:
            # This is a placeholder for actual UI testing
            # In a real scenario, this would interact with the UI using a tool like Selenium or PyAutoGUI
            ui_actions = {
                "open_chat": 0.5,
                "send_message": 0.2,
                "switch_tab": 0.1,
                "open_settings": 0.3,
            }

            return ui_actions
        except Exception as e:
            logger.error("Error measuring UI response time: %s", str(e), exc_info=True)
            return {"error": str(e)}

    def profile_code(self) -> Dict:
        """
        Profile the Atlas application code using cProfile.

        Returns:
            Dict: Profiling results
        """
        logger.info("Profiling Atlas application code")
        try:
            # Profile the main application
            profiler = cProfile.Profile()
            profiler.enable()

            # Replace with actual application launch code
            subprocess.run(
                ["python", "-m", self.app_name],
                timeout=30,
                check=False,
                capture_output=True,
                text=True,
            )

            profiler.disable()
            s = StringIO()
            sortby = pstats.SortKey.CUMULATIVE
            ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
            ps.print_stats(10)  # Print top 10 functions

            return {"top_functions": s.getvalue().splitlines()[:15]}
        except Exception as e:
            logger.error("Error during code profiling: %s", str(e), exc_info=True)
            return {"error": str(e)}

    def generate_report(self, benchmark_results: Dict, profiling_results: Dict) -> None:
        """
        Generate a comprehensive performance report.

        Args:
            benchmark_results: Results from benchmarks
            profiling_results: Results from code profiling
        """
        logger.info("Generating performance audit report")
        report = {
            "environment": self.environment,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "benchmarks": benchmark_results,
            "profiling": profiling_results,
            "recommendations": self.generate_recommendations(
                benchmark_results, profiling_results
            ),
        }

        with open(self.report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info("Performance audit report generated: %s", self.report_file)

    def generate_recommendations(
        self, benchmark_results: Dict, profiling_results: Dict
    ) -> List[str]:
        """
        Generate optimization recommendations based on audit results.

        Args:
            benchmark_results: Results from benchmarks
            profiling_results: Results from code profiling

        Returns:
            List[str]: List of recommendations
        """
        logger.info("Generating optimization recommendations")
        recommendations = []

        # Startup time recommendation
        startup_result = benchmark_results.get("startup_time", {}).get(
            "duration_seconds", -1
        )
        if isinstance(startup_result, (int, float)) and startup_result > 5:
            recommendations.append(
                "Startup time is high (>5s). Consider lazy loading of modules and optimizing initialization code."
            )

        # Memory usage recommendation
        memory_result = benchmark_results.get("memory_usage", {}).get("rss_bytes", 0)
        if memory_result > 500 * 1024 * 1024:  # 500MB
            recommendations.append(
                "Memory usage is high (>500MB). Investigate memory leaks and optimize data structures."
            )

        # CPU usage recommendation
        cpu_result = benchmark_results.get("cpu_usage", {}).get("cpu_percent", 0)
        if cpu_result > 50:
            recommendations.append(
                "CPU usage is high (>50%). Optimize algorithms and check for inefficient loops or polling."
            )

        # Module load time recommendation
        module_times = benchmark_results.get("module_load_time", {})
        for module, load_time in module_times.items():
            if isinstance(load_time, (int, float)) and load_time > 1:
                recommendations.append(
                    f"Module {module} load time is high (>1s). Consider lazy loading or splitting the module."
                )

        # UI response time recommendation
        ui_times = benchmark_results.get("ui_response_time", {})
        for action, response_time in ui_times.items():
            if isinstance(response_time, (int, float)) and response_time > 0.2:
                recommendations.append(
                    f"UI action {action} response time is high (>200ms). Optimize UI rendering and event handling."
                )

        # Profiling-based recommendation
        if "top_functions" in profiling_results:
            recommendations.append(
                "Review the top time-consuming functions in the profiling results for optimization opportunities."
            )

        if not recommendations:
            recommendations.append(
                "No significant performance issues detected. Continue monitoring performance metrics."
            )

        return recommendations

    def run(self) -> bool:
        """
        Execute the full performance audit pipeline.

        Returns:
            bool: True if audit completed successfully, False otherwise
        """
        logger.info(
            "Starting performance audit for Atlas in environment: %s", self.environment
        )
        try:
            if not self.check_prerequisites():
                logger.error("Performance audit prerequisites not met, aborting")
                return False

            benchmark_results = self.run_benchmarks()
            profiling_results = self.profile_code()
            self.generate_report(benchmark_results, profiling_results)

            logger.info(
                "Performance audit completed successfully for environment: %s",
                self.environment,
            )
            return True
        except Exception as e:
            logger.error("Performance audit failed: %s", str(e), exc_info=True)
            return False


def main():
    """Main function to run the performance audit script."""
    parser = argparse.ArgumentParser(description="Performance audit script for Atlas")
    parser.add_argument(
        "--environment",
        "-e",
        default="dev",
        choices=["dev", "staging", "prod"],
        help="Target environment for audit",
    )
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

    args = parser.parse_args()

    # Override log level if specified
    if args.log_level:
        logger.setLevel(getattr(logging, args.log_level.upper(), logging.INFO))

    auditor = AtlasPerformanceAuditor(
        environment=args.environment, config_path=args.config
    )
    success = auditor.run()

    if success:
        logger.info("Performance audit completed successfully")
        sys.exit(0)
    else:
        logger.error("Performance audit failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
