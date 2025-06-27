#!/usr/bin/env python3
"""
Performance Profiler Tool for Atlas
Analyzes code performance, bottlenecks, and optimization opportunities
"""

import ast
import logging
import re
import tracemalloc
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceIssue:
    """Represents a performance issue or optimization opportunity."""

    file_path: str
    line_number: int
    issue_type: str
    severity: str  #'critical', 'high', 'medium', 'low'
    description: str
    suggestion: str
    impact_estimate: str
    code_snippet: str


@dataclass
class FunctionProfile:
    """Performance profile of a function."""

    name: str
    file_path: str
    line_number: int
    call_count: int
    total_time: float
    cumulative_time: float
    per_call_time: float
    complexity_score: int


@dataclass
class PerformanceReport:
    """Complete performance analysis report."""

    issues: List[PerformanceIssue]
    function_profiles: List[FunctionProfile]
    memory_usage: Dict[str, Any]
    system_metrics: Dict[str, Any]
    recommendations: List[str]
    summary: str


class PerformanceProfiler:
    """Advanced performance analyzer for Atlas codebase."""

    def __init__(self, root_path: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root_path = Path(root_path) if root_path else Path(__file__).parent.parent
        self.excluded_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "venv-macos",
            "venv-linux",
            "node_modules",
            ".pytest_cache",
            "build",
            "dist",
            ".mypy_cache",
            "site-packages",
            "lib",
            "include",
            "Scripts",
            "bin",
            "share",
            ".DS_Store",
            "unused",
            "monitoring/logs",
        }

        # Performance issue patterns
        self.performance_patterns = {
            "blocking_calls": {
                "patterns": [
                    r"time\.sleep\(\s*\d+\s*\)",
                    r"input\s*\(",
                    r"requests\.get\([^)]*timeout=None",
                    r"subprocess\.run\([^)]*timeout=None",
                    r"\.join\(\)\s*$",  # Thread joins without timeout
                ],
                "severity": "high",
                "description": "Potentially blocking operation",
                "suggestion": "Consider using async/await or timeouts",
            },
            "inefficient_loops": {
                "patterns": [
                    r"for\s+\w+\s+in\s+range\(len\(",
                    r"while\s+True:(?!\s*#.*break)",
                    r"for.*in.*\.keys\(\):",
                    r"for.*in.*\.values\(\):.*if.*==",
                ],
                "severity": "medium",
                "description": "Inefficient loop pattern",
                "suggestion": "Use enumerate(), direct iteration, or dict methods",
            },
            "memory_inefficient": {
                "patterns": [
                    r"\.append\(.*\)\s*$",  # In loops
                    r"\[\s*\].*for.*in.*for.*in",  # Nested list comprehensions
                    r"\.copy\(\).*\.copy\(\)",  # Multiple copies
                    r"json\.loads\(.*\.read\(\)\)",  # Loading large JSON
                ],
                "severity": "medium",
                "description": "Memory inefficient operation",
                "suggestion": "Consider generators, pre-allocation, or streaming",
            },
            "expensive_operations": {
                "patterns": [
                    r"\.sort\(\).*\.sort\(\)",  # Multiple sorts
                    r"regex\.compile\(.*\).*in.*for",  # Regex in loops
                    r"open\(.*\).*in.*for",  # File operations in loops
                    r"\.find\(.*\).*in.*for",  # String searches in loops
                ],
                "severity": "high",
                "description": "Expensive operation in loop or repeated context",
                "suggestion": "Move expensive operations outside loops or cache results",
            },
            "database_antipatterns": {
                "patterns": [
                    r"\.execute\(.*\).*in.*for",  # Queries in loops
                    r"SELECT \*",  # Select all
                    r"\.fetchall\(\).*len\(",  # Count with fetchall
                ],
                "severity": "critical",
                "description": "Database performance anti-pattern",
                "suggestion": "Use batch operations, specific columns, or COUNT queries",
            },
        }

    def analyze_performance(self, profile_runtime: bool = False) -> PerformanceReport:
        """Perform comprehensive performance analysis."""
        self.logger.info("Starting performance analysis...")

        # 1. Static code analysis for performance issues
        issues = self._analyze_static_performance()

        # 2. System metrics
        system_metrics = self._get_system_metrics()

        # 3. Memory analysis
        memory_usage = self._analyze_memory_usage()

        # 4. Runtime profiling (optional)
        function_profiles = []
        if profile_runtime:
            function_profiles = self._profile_runtime_performance()

        # 5. Generate recommendations
        recommendations = self._generate_performance_recommendations(
            issues, system_metrics
        )

        # 6. Create summary
        summary = self._create_performance_summary(issues, system_metrics, memory_usage)

        return PerformanceReport(
            issues=issues,
            function_profiles=function_profiles,
            memory_usage=memory_usage,
            system_metrics=system_metrics,
            recommendations=recommendations,
            summary=summary,
        )

    def _analyze_static_performance(self) -> List[PerformanceIssue]:
        """Analyze code for static performance issues."""
        issues = []

        # Find all Python files
        python_files = [
            f
            for f in self.root_path.rglob("*.py")
            if not any(excluded in f.parts for excluded in self.excluded_dirs)
        ]

        for file_path in python_files:
            file_issues = self._analyze_file_performance(file_path)
            issues.extend(file_issues)

        return sorted(
            issues,
            key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.severity],
        )

    def _analyze_file_performance(self, file_path: Path) -> List[PerformanceIssue]:
        """Analyze a single file for performance issues."""
        issues = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Pattern-based analysis
            for category, config in self.performance_patterns.items():
                for pattern in config["patterns"]:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            # Check if it's in a loop context for certain patterns
                            in_loop = self._is_in_loop_context(lines, line_num)

                            # Adjust severity based on context
                            severity = config["severity"]
                            description = config["description"]
                            if (
                                category
                                in ["memory_inefficient", "expensive_operations"]
                                and in_loop
                            ):
                                severity = "critical" if severity == "high" else "high"
                                description += " (in loop context)"

                            issue = PerformanceIssue(
                                file_path=str(file_path.relative_to(self.root_path)),
                                line_number=line_num,
                                issue_type=category,
                                severity=severity,
                                description=description,
                                suggestion=config["suggestion"],
                                impact_estimate=self._estimate_impact(
                                    category, in_loop
                                ),
                                code_snippet=line.strip(),
                            )
                            issues.append(issue)

            # AST-based analysis for more complex patterns
            ast_issues = self._analyze_ast_performance(file_path, content)
            issues.extend(ast_issues)

        except Exception as e:
            self.logger.warning(f"Could not analyze performance for {file_path}: {e}")

        return issues

    def _is_in_loop_context(self, lines: List[str], line_num: int) -> bool:
        """Check if a line is within a loop context."""
        # Look backwards for loop keywords
        loop_keywords = ["for ", "while "]
        indent_level = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())

        for i in range(max(0, line_num - 20), line_num):
            line = lines[i]
            line_indent = len(line) - len(line.lstrip())

            if line_indent < indent_level and any(
                keyword in line for keyword in loop_keywords
            ):
                return True

        return False

    def _estimate_impact(self, category: str, in_loop: bool) -> str:
        """Estimate the performance impact of an issue."""
        impact_map = {
            "blocking_calls": "High - Can freeze application",
            "inefficient_loops": "Medium - O(n) to O(n²) increase",
            "memory_inefficient": "Medium - Increased memory usage",
            "expensive_operations": "High - CPU intensive",
            "database_antipatterns": "Critical - Database performance",
        }

        base_impact = impact_map.get(category, "Unknown")
        if in_loop:
            base_impact = (
                "Critical - " + base_impact + " (multiplied by loop iterations)"
            )

        return base_impact

    def _analyze_ast_performance(
        self, file_path: Path, content: str
    ) -> List[PerformanceIssue]:
        """Analyze AST for complex performance patterns."""
        issues = []

        try:
            tree = ast.parse(content)
            analyzer = PerformanceASTAnalyzer(
                str(file_path.relative_to(self.root_path))
            )
            analyzer.visit(tree)
            issues.extend(analyzer.issues)

        except SyntaxError:
            pass  # Skip files with syntax errors
        except Exception as e:
            self.logger.warning(f"AST analysis failed for {file_path}: {e}")

        return issues

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk information
            disk = psutil.disk_usage("/")

            # Process information
            process = psutil.Process()
            process_memory = process.memory_info()

            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None,
                },
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_percent": memory.percent,
                    "swap_used_percent": swap.percent,
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "used_percent": (disk.used / disk.total) * 100,
                },
                "process": {
                    "memory_mb": process_memory.rss / (1024**2),
                    "memory_percent": process.memory_percent(),
                },
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {}

    def _analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        try:
            # Start memory tracing
            tracemalloc.start()

            # Get current memory snapshot
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")

            memory_analysis = {
                "top_memory_allocations": [],
                "total_traced_memory_mb": sum(stat.size for stat in top_stats)
                / (1024**2),
                "allocation_count": len(top_stats),
            }

            # Top memory allocations
            for stat in top_stats[:10]:
                memory_analysis["top_memory_allocations"].append(
                    {
                        "file": stat.traceback.format()[0]
                        if stat.traceback
                        else "Unknown",
                        "size_mb": stat.size / (1024**2),
                        "count": stat.count,
                    }
                )

            return memory_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing memory usage: {e}")
            return {"error": str(e)}

    def _profile_runtime_performance(self) -> List[FunctionProfile]:
        """Profile runtime performance of key functions."""
        profiles = []

        try:
            # This would need to be integrated with actual Atlas runtime
            # For now, return empty list as it requires runtime execution
            self.logger.info("Runtime profiling requires actual execution context")

        except Exception as e:
            self.logger.error(f"Error in runtime profiling: {e}")

        return profiles

    def _generate_performance_recommendations(
        self, issues: List[PerformanceIssue], system_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        # Issue-based recommendations
        critical_issues = [i for i in issues if i.severity == "critical"]
        high_issues = [i for i in issues if i.severity == "high"]

        if critical_issues:
            recommendations.append(
                f"🚨 **URGENT**: Fix {len(critical_issues)} critical performance issues immediately"
            )

        if high_issues:
            recommendations.append(
                f"⚠️ **HIGH PRIORITY**: Address {len(high_issues)} high-impact performance issues"
            )

        # Issue category recommendations
        issue_categories = defaultdict(int)
        for issue in issues:
            issue_categories[issue.issue_type] += 1

        if issue_categories["blocking_calls"] > 0:
            recommendations.append(
                "🔄 **Async Optimization**: Convert blocking calls to async operations"
            )

        if issue_categories["inefficient_loops"] > 0:
            recommendations.append(
                "🔁 **Loop Optimization**: Optimize loop patterns for better performance"
            )

        if issue_categories["database_antipatterns"] > 0:
            recommendations.append(
                "🗄️ **Database Optimization**: Implement database query optimization"
            )

        # System-based recommendations
        if system_metrics.get("memory", {}).get("used_percent", 0) > 80:
            recommendations.append(
                "💾 **Memory Optimization**: High memory usage detected, consider memory optimization"
            )

        if system_metrics.get("cpu", {}).get("usage_percent", 0) > 80:
            recommendations.append(
                "⚡ **CPU Optimization**: High CPU usage detected, profile CPU-intensive operations"
            )

        # General recommendations
        recommendations.extend(
            [
                "📊 **Profiling**: Use cProfile for detailed function-level performance analysis",
                "🔍 **Monitoring**: Implement performance monitoring in production",
                "⚡ **Caching**: Add caching for frequently accessed data",
                "🧪 **Testing**: Add performance regression tests",
            ]
        )

        return recommendations

    def _create_performance_summary(
        self,
        issues: List[PerformanceIssue],
        system_metrics: Dict[str, Any],
        memory_usage: Dict[str, Any],
    ) -> str:
        """Create performance analysis summary."""
        critical_count = len([i for i in issues if i.severity == "critical"])
        high_count = len([i for i in issues if i.severity == "high"])
        medium_count = len([i for i in issues if i.severity == "medium"])
        low_count = len([i for i in issues if i.severity == "low"])

        # Performance score calculation
        performance_score = 100
        performance_score -= critical_count * 25
        performance_score -= high_count * 15
        performance_score -= medium_count * 8
        performance_score -= low_count * 3
        performance_score = max(0, performance_score)

        summary = f"""
📊 PERFORMANCE ANALYSIS SUMMARY
===============================
🎯 Performance Score: {performance_score}/100

🚨 Critical Issues: {critical_count}
⚠️ High Priority: {high_count}
📋 Medium Priority: {medium_count}
💡 Low Priority: {low_count}

💻 SYSTEM STATUS:
CPU Usage: {system_metrics.get("cpu", {}).get("usage_percent", "N/A")}%
Memory Usage: {system_metrics.get("memory", {}).get("used_percent", "N/A")}%
Process Memory: {system_metrics.get("process", {}).get("memory_mb", "N/A"):.1f} MB

🔍 PERFORMANCE ASSESSMENT:
{self._get_performance_assessment(performance_score, critical_count, high_count)}
"""
        return summary.strip()

    def _get_performance_assessment(self, score: int, critical: int, high: int) -> str:
        """Get performance assessment based on score and issues."""
        if score >= 90 and critical == 0:
            return "Excellent performance. Minor optimizations possible."
        if score >= 75 and critical == 0:
            return "Good performance with room for optimization."
        if score >= 50 or critical == 0:
            return "Moderate performance. Optimization recommended."
        return "Poor performance. Immediate optimization required."

    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report."""
        analysis = self.analyze_performance()

        report = []
        report.append("⚡ **Atlas Performance Analysis Report**\n")

        # Summary
        report.append(analysis.summary)
        report.append("")

        # Critical Issues
        critical_issues = [i for i in analysis.issues if i.severity == "critical"]
        if critical_issues:
            report.append("## 🚨 **Critical Performance Issues**")
            for issue in critical_issues[:10]:
                report.append(f"**{issue.file_path}:{issue.line_number}**")
                report.append(f"- **Issue**: {issue.description}")
                report.append(f"- **Impact**: {issue.impact_estimate}")
                report.append(f"- **Code**: `{issue.code_snippet}`")
                report.append(f"- **Fix**: {issue.suggestion}")
                report.append("")

        # Performance Hotspots
        issue_categories = defaultdict(list)
        for issue in analysis.issues:
            issue_categories[issue.issue_type].append(issue)

        if issue_categories:
            report.append("## 🔥 **Performance Hotspots**")
            for category, issues in sorted(
                issue_categories.items(), key=lambda x: len(x[1]), reverse=True
            ):
                report.append(
                    f"**{category.replace('_', ' ').title()}**: {len(issues)} issues"
                )
                # Show top 3 files with most issues in this category
                file_counts = defaultdict(int)
                for issue in issues:
                    file_counts[issue.file_path] += 1

                for file_path, count in sorted(
                    file_counts.items(), key=lambda x: x[1], reverse=True
                )[:3]:
                    report.append(f"  - `{file_path}`: {count} issues")
            report.append("")

        # System Performance
        if analysis.system_metrics:
            report.append("## 💻 **System Performance**")
            cpu = analysis.system_metrics.get("cpu", {})
            memory = analysis.system_metrics.get("memory", {})
            process = analysis.system_metrics.get("process", {})

            report.append(
                f"- **CPU**: {cpu.get('usage_percent', 'N/A')}% usage, {cpu.get('count', 'N/A')} cores"
            )
            report.append(
                f"- **Memory**: {memory.get('used_percent', 'N/A')}% used ({memory.get('available_gb', 'N/A'):.1f}GB available)"
            )
            report.append(
                f"- **Process Memory**: {process.get('memory_mb', 'N/A'):.1f} MB ({process.get('memory_percent', 'N/A'):.1f}%)"
            )
            report.append("")

        # Recommendations
        if analysis.recommendations:
            report.append("## 💡 **Performance Optimization Recommendations**")
            for rec in analysis.recommendations:
                report.append(f"- {rec}")
            report.append("")

        return "\n".join(report)


class PerformanceASTAnalyzer(ast.NodeVisitor):
    """AST analyzer for complex performance patterns."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
        self.loop_depth = 0
        self.function_complexity = defaultdict(int)

    def visit_For(self, node):
        """Analyze for loops."""
        self.loop_depth += 1

        # Check for nested loops
        if self.loop_depth > 2:
            self.issues.append(
                PerformanceIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    issue_type="nested_loops",
                    severity="high",
                    description=f"Deeply nested loop (depth: {self.loop_depth})",
                    suggestion="Consider breaking into separate functions or using more efficient algorithms",
                    impact_estimate="High - O(n³) or worse complexity",
                    code_snippet=f"Nested loop at depth {self.loop_depth}",
                )
            )

        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        """Analyze while loops."""
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_FunctionDef(self, node):
        """Analyze function complexity."""
        # Count decision points
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1

        if complexity > 20:
            self.issues.append(
                PerformanceIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    issue_type="high_complexity",
                    severity="medium",
                    description=f"Function {node.name} has high complexity ({complexity})",
                    suggestion="Break down into smaller functions",
                    impact_estimate="Medium - Affects maintainability and performance",
                    code_snippet=f"def {node.name}(...): #complexity: {complexity}",
                )
            )

        self.generic_visit(node)


# Integration functions
def analyze_performance() -> str:
    """Analyze Atlas performance and return report."""
    profiler = PerformanceProfiler()
    return profiler.generate_performance_report()


def find_performance_issues(severity: str = "all") -> str:
    """Find performance issues of specific severity."""
    profiler = PerformanceProfiler()
    analysis = profiler.analyze_performance()

    issues = (
        [i for i in analysis.issues if i.severity == severity]
        if severity != "all"
        else analysis.issues
    )

    if not issues:
        return f"✅ No {severity} performance issues found."

    report = [f"⚡ **Performance Issues ({severity})**\n"]
    for issue in issues[:20]:  # Limit to top 20
        report.append(f"**{issue.file_path}:{issue.line_number}**")
        report.append(f"- {issue.description}")
        report.append(f"- Impact: {issue.impact_estimate}")
        report.append(f"- Fix: {issue.suggestion}")
        report.append("")

    return "\n".join(report)


if __name__ == "__main__":
    # Test the profiler
    profiler = PerformanceProfiler()
    print(profiler.generate_performance_report())
