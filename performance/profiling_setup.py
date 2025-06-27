"""Performance Profiling Setup for Atlas (ASC-025)

This module sets up profiling tools to audit the performance of the Atlas application as part of ASC-025. It uses cProfile and line_profiler to identify bottlenecks and inefficiencies.
"""

import cProfile
import logging
import os
import pstats

from line_profiler import LineProfiler

# Setup logging
logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """Manages profiling of the Atlas application to identify performance bottlenecks."""

    def __init__(self, output_dir="performance/reports"):
        self.output_dir = output_dir
        self.profiler = cProfile.Profile()
        self.line_profiler = LineProfiler()
        self.is_profiling = False
        os.makedirs(output_dir, exist_ok=True)
        logger.info(
            f"PerformanceProfiler initialized with output directory: {output_dir}"
        )

    def start_profiling(self):
        """Start profiling the application."""
        self.profiler.enable()
        self.is_profiling = True
        logger.info("Profiling started")

    def stop_profiling(self, output_file="profile_stats.txt"):
        """Stop profiling and save results to a file.

        Args:
            output_file (str): The file to save profiling stats to.
        """
        if not self.is_profiling:
            logger.warning("Profiling not started, cannot stop")
            return

        self.profiler.disable()
        self.is_profiling = False
        output_path = os.path.join(self.output_dir, output_file)
        with open(output_path, "w") as f:
            ps = pstats.Stats(self.profiler, stream=f)
            ps.sort_stats("cumulative")
            ps.print_stats()
        logger.info(f"Profiling stopped, results saved to {output_path}")

    def profile_function(self, func):
        """Decorator to profile a specific function using line_profiler.

        Args:
            func: The function to profile.

        Returns:
            function: Wrapped function with profiling.
        """
        self.line_profiler.add_function(func)
        logger.info(f"Function {func.__name__} added for line profiling")
        return self.line_profiler.wrap_function(func)

    def start_line_profiling(self):
        """Start line profiling for added functions."""
        self.line_profiler.enable_by_count()
        logger.info("Line profiling started")

    def stop_line_profiling(self, output_file="line_profile_stats.txt"):
        """Stop line profiling and save results.

        Args:
            output_file (str): The file to save line profiling stats to.
        """
        self.line_profiler.disable_by_count()
        output_path = os.path.join(self.output_dir, output_file)
        with open(output_path, "w") as f:
            self.line_profiler.print_stats(stream=f)
        logger.info(f"Line profiling stopped, results saved to {output_path}")
