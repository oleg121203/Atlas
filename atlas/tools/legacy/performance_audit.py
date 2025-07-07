"""
Performance Audit Tool for Atlas.
This script analyzes application responsiveness, identifies bottlenecks, and logs performance metrics.
"""

import asyncio
import os
import time
import tracemalloc
from typing import Any, Dict, List

import psutil
import sentry_sdk


class PerformanceAuditor:
    """
    A class to conduct performance audits on Atlas application, focusing on response times and memory usage.
    """

    def __init__(self, log_file: str = "performance_audit.log") -> None:
        """
        Initialize the PerformanceAuditor with a log file for storing results.

        Args:
            log_file (str): Path to the log file for audit results.
        """
        self.log_file = log_file
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        tracemalloc.start()

    def log(self, message: str) -> None:
        """
        Log a message to the specified log file with timestamp.

        Args:
            message (str): Message to log.
        """
        with open(self.log_file, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

    def measure_cpu_usage(self) -> float:
        """
        Measure current CPU usage of the process.

        Returns:
            float: CPU usage percentage.
        """
        return self.process.cpu_percent(interval=1)

    def measure_memory_usage(self) -> Dict[str, float]:
        """
        Measure current memory usage of the process.

        Returns:
            Dict[str, float]: Dictionary with memory usage stats in MB.
        """
        mem_info = self.process.memory_info()
        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics("lineno")

        return {
            "rss": mem_info.rss / 1024 / 1024,  # Resident Set Size in MB
            "vms": mem_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            "peak": stats[0].size / 1024 / 1024
            if stats
            else 0.0,  # Peak memory from tracemalloc
        }

    async def measure_response_time(
        self, func: callable, *args, **kwargs
    ) -> Dict[str, Any]:
        """
        Measure response time of a given async function.

        Args:
            func (callable): Function to measure.
            *args, **kwargs: Arguments to pass to the function.

        Returns:
            Dict[str, Any]: Dictionary with execution time and result.
        """
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        return {
            "execution_time": execution_time,
            "result": result,
            "function": func.__name__,
        }

    def report(
        self,
        test_name: str,
        cpu: float,
        memory: Dict[str, float],
        response_times: List[Dict[str, Any]],
    ) -> None:
        """
        Generate a performance report for the given test.

        Args:
            test_name (str): Name of the test being reported.
            cpu (float): CPU usage percentage.
            memory (Dict[str, float]): Memory usage stats.
            response_times (List[Dict[str, Any]]): List of response time measurements.
        """
        self.log(f"=== Performance Report for {test_name} ===")
        self.log(f"CPU Usage: {cpu:.2f}%")
        self.log(
            f"Memory Usage - RSS: {memory['rss']:.2f} MB, VMS: {memory['vms']:.2f} MB, Peak: {memory['peak']:.2f} MB"
        )
        for rt in response_times:
            self.log(
                f"Function {rt['function']} - Execution Time: {rt['execution_time']:.4f} seconds"
            )
        self.log(f"=== End of Report for {test_name} ===\n")

        # Also send performance data to Sentry if initialized
        if sentry_sdk.Hub.current.client:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("audit_type", "performance")
                scope.set_tag("test_name", test_name)
                scope.set_extra("cpu_usage", cpu)
                scope.set_extra("memory_usage", memory)
                for rt in response_times:
                    scope.set_extra(
                        f"response_time_{rt['function']}", rt["execution_time"]
                    )
                sentry_sdk.capture_message(f"Performance audit for {test_name}")


# Example usage
if __name__ == "__main__":
    auditor = PerformanceAuditor()

    # Simulate some async functions to test
    async def simulate_ui_response():
        await asyncio.sleep(0.1)  # Simulate UI rendering delay
        return "UI Rendered"

    async def simulate_db_query():
        await asyncio.sleep(0.5)  # Simulate database query delay
        return "Data Fetched"

    async def run_audit():
        cpu_usage = auditor.measure_cpu_usage()
        memory_usage = auditor.measure_memory_usage()

        response_times = []
        response_times.append(await auditor.measure_response_time(simulate_ui_response))
        response_times.append(await auditor.measure_response_time(simulate_db_query))

        auditor.report("Initial App Load", cpu_usage, memory_usage, response_times)

    asyncio.run(run_audit())
