"""Code Profiler Tool for Atlas

Provides profiling capabilities to identify performance bottlenecks in code.
"""

import cProfile
import io
import logging
import pstats
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class CodeProfiler:
    """Code profiling tool for performance analysis.

    Provides methods to profile Python code execution and identify bottlenecks.
    Can be used as a decorator or context manager.
    """

    def __init__(self, name: str = "profile", sort_by: str = "cumulative"):
        """Initialize the code profiler.

        Args:
            name: Name of the profile for identification in reports
            sort_by: Sorting method for profile results (cumulative, time, calls, etc.)
        """
        self.name = name
        self.sort_by = sort_by
        self.profiler = cProfile.Profile()
        self.results: Optional[pstats.Stats] = None
        logger.debug(f"CodeProfiler '{name}' initialized")

    def __enter__(self):
        """Start profiling when used as a context manager."""
        self.profiler.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop profiling when exiting context manager."""
        self.profiler.disable()
        self.results = pstats.Stats(self.profiler)
        self.results.sort_stats(self.sort_by)

    def __call__(self, func):
        """Allow use as a decorator."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def run(self, code: Union[str, Callable], *args, **kwargs) -> Any:
        """Run and profile a callable or code string.

        Args:
            code: Callable function or code string to profile
            *args: Arguments to pass to the callable
            **kwargs: Keyword arguments to pass to the callable

        Returns:
            Result of the callable or None for code strings
        """
        self.profiler.enable()
        result = None

        try:
            result = (
                code(*args, **kwargs)
                if callable(code)
                else exec(code, globals(), locals())
            )
        finally:
            self.profiler.disable()
            self.results = pstats.Stats(self.profiler)
            self.results.sort_stats(self.sort_by)

        return result

    def print_stats(self, lines: int = 20):
        """Print profile statistics to stdout.

        Args:
            lines: Number of lines to print
        """
        if self.results:
            print(f"\n--- Profile: {self.name} ---")
            self.results.print_stats(lines)

    def get_stats(self, lines: int = 20) -> str:
        """Get profile statistics as a string.

        Args:
            lines: Number of lines to include

        Returns:
            String containing formatted profile statistics
        """
        if not self.results:
            return "No profile results available"

        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats(self.sort_by)
        ps.print_stats(lines)
        return s.getvalue()

    def get_top_functions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the top functions by time consumption.

        Args:
            limit: Maximum number of functions to return

        Returns:
            List of dictionaries with function stats
        """
        if not self.results:
            return []

        result = []
        stats = self.results.stats
        items = [(key, stats[key]) for key in stats]
        items.sort(key=lambda item: item[1][2], reverse=True)  # Sort by cumulative time

        for i, (func, (_cc, nc, tt, ct, _callers)) in enumerate(items[:limit]):
            if i >= limit:
                break

            file_path, line, func_name = func
            result.append(
                {
                    "file": file_path,
                    "line": line,
                    "function": func_name,
                    "calls": nc,  # Number of calls
                    "total_time": tt,  # Total time
                    "cumulative_time": ct,  # Cumulative time
                    "time_per_call": tt / nc if nc > 0 else 0,
                }
            )

        return result

    def identify_bottlenecks(self, threshold_ms: float = 100.0) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks.

        Args:
            threshold_ms: Time threshold in milliseconds to consider as bottleneck

        Returns:
            List of bottlenecks with function details and time statistics
        """
        bottlenecks = []
        threshold_sec = threshold_ms / 1000.0

        if not self.results:
            return bottlenecks

        top_funcs = self.get_top_functions(limit=30)  # Get more functions to analyze

        for func in top_funcs:
            # Check if this function is a bottleneck
            if func["time_per_call"] > threshold_sec:
                bottlenecks.append(
                    {
                        **func,
                        "is_bottleneck": True,
                        "threshold_exceeded": func["time_per_call"] / threshold_sec,
                        "suggested_action": "Optimize or cache results",
                    }
                )

        return bottlenecks


def profile_function(func=None, *, name=None, print_results=True):
    """Decorator to profile a function.

    Args:
        func: Function to profile
        name: Optional name for the profile
        print_results: Whether to print results after execution

    Returns:
        Decorated function
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            profile_name = name or f.__name__
            profiler = CodeProfiler(name=profile_name)
            result = profiler.run(f, *args, **kwargs)

            if print_results:
                profiler.print_stats()

                # Log bottlenecks
                bottlenecks = profiler.identify_bottlenecks()
                if bottlenecks:
                    logger.warning(
                        f"Found {len(bottlenecks)} bottlenecks in {profile_name}"
                    )
                    for b in bottlenecks:
                        logger.warning(
                            f"Bottleneck: {b['function']} in {b['file']}:{b['line']} - "
                            f"{b['time_per_call'] * 1000:.2f}ms per call"
                        )

            return result

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def profile_code_block(code_str: str, name: str = "code_block") -> Dict[str, Any]:
    """Profile a block of code provided as a string.

    Args:
        code_str: Python code as a string
        name: Name for the profile

    Returns:
        Dictionary with profiling results
    """
    profiler = CodeProfiler(name=name)
    start_time = time.time()

    try:
        # Execute the code
        profiler.run(code_str)
        execution_time = time.time() - start_time

        # Get bottlenecks and stats
        bottlenecks = profiler.identify_bottlenecks()
        stats = profiler.get_stats(lines=30)
        top_functions = profiler.get_top_functions(limit=10)

        return {
            "success": True,
            "execution_time": execution_time,
            "bottlenecks": bottlenecks,
            "top_functions": top_functions,
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Error profiling code block: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "execution_time": time.time() - start_time,
        }


class FunctionTimer:
    """Simple timer for measuring function execution time.

    Can be used as a decorator or context manager.
    """

    def __init__(self, name: str = "timer"):
        """Initialize the function timer.

        Args:
            name: Name for the timer
        """
        self.name = name
        self.start_time = 0.0
        self.end_time = 0.0
        self.elapsed = 0.0

    def __enter__(self):
        """Start timing when used as a context manager."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing when exiting context manager."""
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        logger.debug(f"{self.name}: {self.elapsed * 1000:.2f}ms")

    def __call__(self, func):
        """Allow use as a decorator."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


# Make the profile function available at module level
profile = profile_function
