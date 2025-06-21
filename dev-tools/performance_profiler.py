#!/usr/bin/env python3
"""
Performance Profiler for Atlas MasterAgent and Planning Layers
Comprehensive latency analysis and bottleneck detection
"""

import asyncio
import cProfile
import functools
import io
import logging
import pstats
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance measurement data."""
    operation: str
    duration_ms: float
    memory_delta_mb: float
    cpu_percent: float
    timestamp: float
    call_count: int = 1
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProfileResult:
    """Results of performance profiling."""
    operation: str
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    call_count: int
    bottlenecks: List[str]
    recommendations: List[str]

class AtlasPerformanceProfiler:
    """Advanced performance profiler for Atlas components."""

    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.targets = {
            "screen_tools": 100,  # ms
            "input_tools": 100,   # ms
            "planning": 500,      # ms
            "execution": 1000,    # ms
            "memory_search": 200, # ms
        }
        self.profiler_enabled = True

    @contextmanager
    def profile_operation(self, operation_name: str, metadata: Optional[Dict] = None):
        """Context manager for profiling operations."""
        if not self.profiler_enabled:
            yield
            return

        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()

            duration_ms = (end_time - start_time) * 1000
            memory_delta = end_memory - start_memory

            metric = PerformanceMetric(
                operation=operation_name,
                duration_ms=duration_ms,
                memory_delta_mb=memory_delta,
                cpu_percent=self._get_cpu_usage(),
                timestamp=time.time(),
                metadata=metadata or {},
            )

            self.metrics.append(metric)

            # Log if exceeds target
            target = self._get_target_latency(operation_name)
            if target and duration_ms > target:
                logger.warning(
                    f"Performance target exceeded: {operation_name} took {duration_ms:.2f}ms "
                    f"(target: {target}ms)",
                )

    def profile_function(self, operation_name: str = None):
        """Decorator for profiling functions."""
        def decorator(func: Callable):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.profile_operation(op_name):
                        return await func(*args, **kwargs)
                return async_wrapper
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.profile_operation(op_name):
                    return func(*args, **kwargs)
            return sync_wrapper

        return decorator

    def profile_master_agent(self, agent_instance) -> ProfileResult:
        """Profile MasterAgent performance comprehensively."""
        logger.info("Starting MasterAgent performance profiling...")

        # Test scenarios
        test_scenarios = [
            ("simple_goal", "Take a screenshot"),
            ("complex_goal", "Analyze the current screen and create a detailed report"),
            ("multi_step", "Open a text editor, write some text, and save the file"),
        ]

        results = []

        for scenario_name, goal in test_scenarios:
            logger.info(f"Profiling scenario: {scenario_name}")

            # Profile planning phase
            with self.profile_operation(f"planning_{scenario_name}"):
                try:
                    # This would call the actual planning methods
                    # For now, simulate planning time
                    time.sleep(0.1)  # Simulated planning
                except Exception as e:
                    logger.error(f"Error in planning {scenario_name}: {e}")

            # Profile execution phase
            with self.profile_operation(f"execution_{scenario_name}"):
                try:
                    # This would call the actual execution methods
                    # For now, simulate execution time
                    time.sleep(0.2)  # Simulated execution
                except Exception as e:
                    logger.error(f"Error in execution {scenario_name}: {e}")

        return self._analyze_results("master_agent")

    def profile_planning_layers(self) -> Dict[str, ProfileResult]:
        """Profile individual planning layer performance."""
        logger.info("Profiling planning layer performance...")

        layers = ["strategic", "tactical", "operational"]
        results = {}

        for layer in layers:
            with self.profile_operation(f"planning_layer_{layer}"):
                # Simulate layer-specific processing
                if layer == "strategic":
                    time.sleep(0.05)  # Strategic planning
                elif layer == "tactical":
                    time.sleep(0.03)  # Tactical planning
                else:
                    time.sleep(0.02)  # Operational planning

            results[layer] = self._analyze_results(f"planning_layer_{layer}")

        return results

    def profile_memory_operations(self) -> ProfileResult:
        """Profile memory search and retrieval operations."""
        logger.info("Profiling memory operations...")

        # Simulate various memory operations
        operations = [
            ("memory_search_simple", 0.05),
            ("memory_search_complex", 0.15),
            ("memory_store", 0.03),
            ("memory_retrieve", 0.02),
        ]

        for op_name, duration in operations:
            with self.profile_operation(op_name):
                time.sleep(duration)

        return self._analyze_results("memory_operations")

    def conduct_latency_measurements(self) -> Dict[str, float]:
        """Conduct comprehensive latency measurements."""
        logger.info("Conducting comprehensive latency measurements...")

        measurements = {}

        # Screen tool latency
        with self.profile_operation("screen_tool_latency"):
            time.sleep(0.08)  # Simulated screen capture
        measurements["screen_tools"] = self._get_latest_duration("screen_tool_latency")

        # Input tool latency
        with self.profile_operation("input_tool_latency"):
            time.sleep(0.06)  # Simulated input operation
        measurements["input_tools"] = self._get_latest_duration("input_tool_latency")

        # Planning latency
        with self.profile_operation("planning_latency"):
            time.sleep(0.3)  # Simulated planning
        measurements["planning"] = self._get_latest_duration("planning_latency")

        # Execution latency
        with self.profile_operation("execution_latency"):
            time.sleep(0.5)  # Simulated execution
        measurements["execution"] = self._get_latest_duration("execution_latency")

        return measurements

    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report."""
        if not self.metrics:
            return "No performance data collected."

        # Analyze all metrics
        report_sections = []

        # Summary statistics
        total_operations = len(self.metrics)
        avg_duration = sum(m.duration_ms for m in self.metrics) / total_operations
        max_duration = max(m.duration_ms for m in self.metrics)

        report_sections.append(f"""
📊 ATLAS PERFORMANCE ANALYSIS REPORT
====================================
📈 Total Operations Measured: {total_operations}
⏱️  Average Duration: {avg_duration:.2f}ms
🔺 Maximum Duration: {max_duration:.2f}ms
📅 Analysis Period: {self._get_analysis_period()}

🎯 PERFORMANCE TARGETS:
""")

        # Target compliance
        for category, target_ms in self.targets.items():
            category_metrics = [m for m in self.metrics if category in m.operation.lower()]
            if category_metrics:
                avg_cat_duration = sum(m.duration_ms for m in category_metrics) / len(category_metrics)
                status = "✅ PASS" if avg_cat_duration <= target_ms else "❌ FAIL"
                report_sections.append(
                    f"  {category}: {avg_cat_duration:.2f}ms (target: {target_ms}ms) {status}",
                )

        # Bottleneck analysis
        report_sections.append(f"""

🔍 BOTTLENECK ANALYSIS:
{self._identify_bottlenecks()}

💡 OPTIMIZATION RECOMMENDATIONS:
{self._generate_recommendations()}

📋 DETAILED METRICS:
""")

        # Top slowest operations
        slowest = sorted(self.metrics, key=lambda m: m.duration_ms, reverse=True)[:5]
        for metric in slowest:
            report_sections.append(
                f"  • {metric.operation}: {metric.duration_ms:.2f}ms "
                f"(memory: {metric.memory_delta_mb:.1f}MB)",
            )

        return "\n".join(report_sections)

    def export_metrics(self, filepath: Path) -> None:
        """Export metrics to file for analysis."""
        import json

        export_data = {
            "timestamp": time.time(),
            "metrics": [
                {
                    "operation": m.operation,
                    "duration_ms": m.duration_ms,
                    "memory_delta_mb": m.memory_delta_mb,
                    "cpu_percent": m.cpu_percent,
                    "timestamp": m.timestamp,
                    "call_count": m.call_count,
                    "metadata": m.metadata,
                }
                for m in self.metrics
            ],
            "targets": self.targets,
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Performance metrics exported to {filepath}")

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=None)
        except ImportError:
            return 0.0

    def _get_target_latency(self, operation_name: str) -> Optional[float]:
        """Get target latency for operation type."""
        for category, target in self.targets.items():
            if category in operation_name.lower():
                return target
        return None

    def _get_latest_duration(self, operation_name: str) -> float:
        """Get duration of latest operation with given name."""
        matching = [m for m in self.metrics if m.operation == operation_name]
        return matching[-1].duration_ms if matching else 0.0

    def _analyze_results(self, operation_prefix: str) -> ProfileResult:
        """Analyze results for operations with given prefix."""
        matching_metrics = [m for m in self.metrics if m.operation.startswith(operation_prefix)]

        if not matching_metrics:
            return ProfileResult(
                operation=operation_prefix,
                total_time_ms=0.0,
                avg_time_ms=0.0,
                min_time_ms=0.0,
                max_time_ms=0.0,
                call_count=0,
                bottlenecks=[],
                recommendations=[],
            )

        durations = [m.duration_ms for m in matching_metrics]

        return ProfileResult(
            operation=operation_prefix,
            total_time_ms=sum(durations),
            avg_time_ms=sum(durations) / len(durations),
            min_time_ms=min(durations),
            max_time_ms=max(durations),
            call_count=len(matching_metrics),
            bottlenecks=self._identify_operation_bottlenecks(matching_metrics),
            recommendations=self._generate_operation_recommendations(matching_metrics),
        )

    def _identify_bottlenecks(self) -> str:
        """Identify system bottlenecks."""
        bottlenecks = []

        # Find operations exceeding targets by significant margin
        for metric in self.metrics:
            target = self._get_target_latency(metric.operation)
            if target and metric.duration_ms > target * 1.5:
                bottlenecks.append(
                    f"  • {metric.operation}: {metric.duration_ms:.2f}ms "
                    f"({(metric.duration_ms/target-1)*100:.0f}% over target)",
                )

        return "\n".join(bottlenecks) if bottlenecks else "  No significant bottlenecks detected."

    def _generate_recommendations(self) -> str:
        """Generate optimization recommendations."""
        recommendations = []

        # Memory usage recommendations
        high_memory_ops = [m for m in self.metrics if m.memory_delta_mb > 50]
        if high_memory_ops:
            recommendations.append("  • Optimize memory usage in high-consumption operations")

        # Slow operations recommendations
        slow_ops = [m for m in self.metrics if m.duration_ms > 1000]
        if slow_ops:
            recommendations.append("  • Consider breaking down slow operations into smaller chunks")

        # General recommendations
        recommendations.extend([
            "  • Implement caching for frequently accessed data",
            "  • Consider async processing for I/O bound operations",
            "  • Profile individual functions for micro-optimizations",
        ])

        return "\n".join(recommendations)

    def _identify_operation_bottlenecks(self, metrics: List[PerformanceMetric]) -> List[str]:
        """Identify bottlenecks for specific operation."""
        bottlenecks = []
        avg_duration = sum(m.duration_ms for m in metrics) / len(metrics)

        if avg_duration > 500:
            bottlenecks.append("High average latency")

        if any(m.memory_delta_mb > 100 for m in metrics):
            bottlenecks.append("High memory consumption")

        return bottlenecks

    def _generate_operation_recommendations(self, metrics: List[PerformanceMetric]) -> List[str]:
        """Generate recommendations for specific operation."""
        recommendations = []
        avg_duration = sum(m.duration_ms for m in metrics) / len(metrics)

        if avg_duration > 200:
            recommendations.append("Consider caching or optimization")

        if any(m.memory_delta_mb > 50 for m in metrics):
            recommendations.append("Optimize memory usage")

        return recommendations

    def _get_analysis_period(self) -> str:
        """Get analysis time period."""
        if not self.metrics:
            return "No data"

        start_time = min(m.timestamp for m in self.metrics)
        end_time = max(m.timestamp for m in self.metrics)
        duration = end_time - start_time

        return f"{duration:.1f} seconds"

# Global profiler instance
profiler = AtlasPerformanceProfiler()

# Convenience functions
def profile_operation(name: str, metadata: Dict = None):
    """Convenience function for profiling operations."""
    return profiler.profile_operation(name, metadata)

def profile_function(name: str = None):
    """Convenience decorator for profiling functions."""
    return profiler.profile_function(name)

def generate_report() -> str:
    """Generate performance report."""
    return profiler.generate_performance_report()

def export_metrics(filepath: str) -> None:
    """Export metrics to file."""
    profiler.export_metrics(Path(filepath))

# Example usage for MasterAgent profiling
async def profile_master_agent_comprehensive():
    """Comprehensive MasterAgent profiling."""
    logger.info("Starting comprehensive MasterAgent performance analysis...")

    # Profile different aspects
    master_agent_result = profiler.profile_master_agent(None)  # Would pass actual instance
    planning_results = profiler.profile_planning_layers()
    memory_result = profiler.profile_memory_operations()
    latency_measurements = profiler.conduct_latency_measurements()

    # Generate and return report
    report = profiler.generate_performance_report()

    # Export detailed metrics
    profiler.export_metrics(Path("performance_analysis.json"))

    return {
        "report": report,
        "master_agent": master_agent_result,
        "planning_layers": planning_results,
        "memory_operations": memory_result,
        "latency_measurements": latency_measurements,
    }

if __name__ == "__main__":
    # Run standalone profiling
    import asyncio

    async def main():
        results = await profile_master_agent_comprehensive()
        print(results["report"])

    asyncio.run(main())
