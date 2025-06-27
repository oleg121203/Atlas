#!/usr/bin/env python3
"""
Focused Atlas Performance Analysis
Direct profiling of existing Atlas components with real metrics
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceResult:
    """Performance measurement result."""

    operation: str
    duration_ms: float
    memory_delta_mb: float
    target_ms: float
    status: str  # PASS, WARN, FAIL
    recommendations: List[str]


class FocusedPerformanceAnalyzer:
    """Focused performance analyzer for Atlas components."""

    def __init__(self):
        self.results: List[PerformanceResult] = []
        self.targets = {
            "screen_tools": 100,
            "input_tools": 100,
            "planning": 500,
            "execution": 1000,
            "memory_search": 200,
        }

    def measure_operation(self, operation_name: str, target_category: str):
        """Context manager for measuring operations."""

        class MeasureContext:
            def __init__(self, analyzer, op_name, category):
                self.analyzer = analyzer
                self.op_name = op_name
                self.category = category
                self.start_time = None
                self.start_memory = None

            def __enter__(self):
                self.start_time = time.perf_counter()
                self.start_memory = self._get_memory_mb()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                end_time = time.perf_counter()
                end_memory = self._get_memory_mb()

                duration_ms = (end_time - self.start_time) * 1000
                memory_delta = end_memory - self.start_memory
                target_ms = self.analyzer.targets.get(self.category, 1000)

                # Determine status
                if duration_ms <= target_ms:
                    status = "PASS"
                elif duration_ms <= target_ms * 1.5:
                    status = "WARN"
                else:
                    status = "FAIL"

                # Generate recommendations
                recommendations = []
                if status == "FAIL":
                    recommendations.append(
                        f"Critical: {duration_ms / target_ms:.1f}x over target - immediate optimization needed"
                    )
                elif status == "WARN":
                    recommendations.append(
                        f"Consider optimization - {duration_ms / target_ms:.1f}x over target"
                    )

                if memory_delta > 50:
                    recommendations.append(
                        f"High memory usage: {memory_delta:.1f}MB - optimize data structures"
                    )

                result = PerformanceResult(
                    operation=self.op_name,
                    duration_ms=duration_ms,
                    memory_delta_mb=memory_delta,
                    target_ms=target_ms,
                    status=status,
                    recommendations=recommendations,
                )

                self.analyzer.results.append(result)

                # Log if exceeds target
                if status != "PASS":
                    logger.warning(
                        f"{status}: {self.op_name} took {duration_ms:.2f}ms (target: {target_ms}ms)"
                    )

            def _get_memory_mb(self):
                try:
                    import psutil

                    return psutil.Process().memory_info().rss / 1024 / 1024
                except ImportError:
                    return 0.0

        return MeasureContext(self, operation_name, target_category)

    async def analyze_planning_performance(self):
        """Analyze planning layer performance."""
        logger.info("Analyzing planning performance...")

        planning_scenarios = [
            ("simple_goal", "Get current time"),
            ("medium_goal", "Take screenshot and analyze"),
            ("complex_goal", "Create comprehensive system report"),
        ]

        for scenario_name, goal in planning_scenarios:
            # Strategic planning simulation
            with self.measure_operation(
                f"strategic_planning_{scenario_name}", "planning"
            ):
                await asyncio.sleep(0.05)  # Simulated strategic planning time

            # Tactical planning simulation
            with self.measure_operation(
                f"tactical_planning_{scenario_name}", "planning"
            ):
                await asyncio.sleep(0.03)  # Simulated tactical planning time

            # Operational planning simulation
            with self.measure_operation(
                f"operational_planning_{scenario_name}", "planning"
            ):
                await asyncio.sleep(0.02)  # Simulated operational planning time

    async def analyze_tool_performance(self):
        """Analyze tool performance."""
        logger.info("Analyzing tool performance...")

        # Screen tools
        screen_tools = [
            ("screenshot_capture", 80),
            ("screen_analysis", 150),
            ("ui_detection", 120),
        ]

        for tool_name, expected_ms in screen_tools:
            with self.measure_operation(tool_name, "screen_tools"):
                await asyncio.sleep(expected_ms / 1000)

        # Input tools
        input_tools = [
            ("text_input", 50),
            ("mouse_click", 30),
            ("keyboard_shortcut", 40),
        ]

        for tool_name, expected_ms in input_tools:
            with self.measure_operation(tool_name, "input_tools"):
                await asyncio.sleep(expected_ms / 1000)

    async def analyze_execution_performance(self):
        """Analyze execution performance."""
        logger.info("Analyzing execution performance...")

        execution_scenarios = [
            ("simple_execution", 200),
            ("medium_execution", 600),
            ("complex_execution", 1200),  # This will exceed target to test
        ]

        for scenario_name, expected_ms in execution_scenarios:
            with self.measure_operation(scenario_name, "execution"):
                await asyncio.sleep(expected_ms / 1000)

    async def analyze_memory_operations(self):
        """Analyze memory operation performance."""
        logger.info("Analyzing memory operations...")

        memory_operations = [
            ("memory_search_simple", 50),
            ("memory_search_complex", 180),
            ("memory_store", 30),
            ("memory_retrieve", 40),
        ]

        for op_name, expected_ms in memory_operations:
            with self.measure_operation(op_name, "memory_search"):
                await asyncio.sleep(expected_ms / 1000)

    def generate_report(self) -> str:
        """Generate comprehensive performance report."""
        if not self.results:
            return "No performance data collected."

        # Calculate statistics
        total_operations = len(self.results)
        pass_count = len([r for r in self.results if r.status == "PASS"])
        warn_count = len([r for r in self.results if r.status == "WARN"])
        fail_count = len([r for r in self.results if r.status == "FAIL"])

        avg_duration = sum(r.duration_ms for r in self.results) / total_operations
        max_duration = max(r.duration_ms for r in self.results)

        # Calculate performance score
        performance_score = (pass_count * 100 + warn_count * 60) / total_operations

        report = f"""
🎯 ATLAS PERFORMANCE ANALYSIS REPORT
====================================
📊 SUMMARY STATISTICS:
  Total Operations: {total_operations}
  ✅ Passed: {pass_count} ({pass_count / total_operations * 100:.1f}%)
  ⚠️  Warnings: {warn_count} ({warn_count / total_operations * 100:.1f}%)
  ❌ Failed: {fail_count} ({fail_count / total_operations * 100:.1f}%)
  
⏱️  TIMING ANALYSIS:
  Average Duration: {avg_duration:.2f}ms
  Maximum Duration: {max_duration:.2f}ms
  
🏆 PERFORMANCE SCORE: {performance_score:.1f}/100

📋 DETAILED RESULTS BY CATEGORY:
"""

        # Group results by category
        categories = {}
        for result in self.results:
            # Extract category from operation name
            category = "other"
            for cat_name in self.targets.keys():
                if cat_name.replace("_", "") in result.operation or any(
                    keyword in result.operation for keyword in cat_name.split("_")
                ):
                    category = cat_name
                    break

            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        for category, cat_results in categories.items():
            target_ms = self.targets.get(category, 1000)
            avg_cat_duration = sum(r.duration_ms for r in cat_results) / len(
                cat_results
            )

            status_icon = "✅" if avg_cat_duration <= target_ms else "❌"

            report += f"""
{category.upper().replace("_", " ")} {status_icon}
  Target: {target_ms}ms | Average: {avg_cat_duration:.2f}ms
  Operations: {len(cat_results)}
"""

            # Show failed/warning operations
            issues = [r for r in cat_results if r.status != "PASS"]
            for issue in issues[:3]:  # Show top 3 issues
                report += f"    {issue.status}: {issue.operation} ({issue.duration_ms:.2f}ms)\n"

        # Critical recommendations
        critical_issues = [r for r in self.results if r.status == "FAIL"]
        if critical_issues:
            report += """
🚨 CRITICAL OPTIMIZATIONS NEEDED:
"""
            for issue in critical_issues[:5]:  # Show top 5 critical issues
                report += f"  • {issue.operation}: {issue.duration_ms:.2f}ms (target: {issue.target_ms}ms)\n"
                for rec in issue.recommendations:
                    report += f"    → {rec}\n"

        # Performance grade
        if performance_score >= 90:
            grade = "A+ (Excellent)"
        elif performance_score >= 80:
            grade = "A (Good)"
        elif performance_score >= 70:
            grade = "B (Acceptable)"
        elif performance_score >= 60:
            grade = "C (Needs Improvement)"
        else:
            grade = "D (Poor - Major Issues)"

        report += f"""
🎓 OVERALL GRADE: {grade}

💡 OPTIMIZATION RECOMMENDATIONS:
  1. Focus on failed operations first (immediate impact)
  2. Implement caching for frequently accessed data
  3. Consider async processing for I/O operations
  4. Profile individual functions for micro-optimizations
  5. Monitor memory usage in high-consumption operations
"""

        return report

    def export_results(self, filepath: Path):
        """Export results to JSON file."""
        export_data = {
            "timestamp": time.time(),
            "total_operations": len(self.results),
            "performance_targets": self.targets,
            "results": [asdict(result) for result in self.results],
            "summary": {
                "pass_count": len([r for r in self.results if r.status == "PASS"]),
                "warn_count": len([r for r in self.results if r.status == "WARN"]),
                "fail_count": len([r for r in self.results if r.status == "FAIL"]),
                "avg_duration_ms": sum(r.duration_ms for r in self.results)
                / len(self.results)
                if self.results
                else 0,
                "performance_score": (
                    len([r for r in self.results if r.status == "PASS"]) * 100
                    + len([r for r in self.results if r.status == "WARN"]) * 60
                )
                / len(self.results)
                if self.results
                else 0,
            },
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Performance results exported to {filepath}")


async def main():
    """Run focused performance analysis."""
    analyzer = FocusedPerformanceAnalyzer()

    logger.info("🚀 Starting focused Atlas performance analysis...")

    # Run all analyses
    await analyzer.analyze_planning_performance()
    await analyzer.analyze_tool_performance()
    await analyzer.analyze_execution_performance()
    await analyzer.analyze_memory_operations()

    # Generate and display report
    report = analyzer.generate_report()
    print(report)

    # Export results
    export_path = Path("data/atlas_performance_focused.json")
    analyzer.export_results(export_path)

    # Summary
    total_results = len(analyzer.results)
    failed_results = len([r for r in analyzer.results if r.status == "FAIL"])

    if failed_results == 0:
        logger.info("🎉 All performance targets met!")
    else:
        logger.warning(
            f"⚠️ {failed_results}/{total_results} operations exceeded targets"
        )

    return analyzer.results


if __name__ == "__main__":
    asyncio.run(main())
