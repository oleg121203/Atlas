"""Unit tests for the CodeProfiler tool.

Tests the code profiling functionality for performance analysis.
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from tools.code_profiler import (
    CodeProfiler,
    FunctionTimer,
    profile_code_block,
    profile_function,
)


# Test function to profile
def slow_function(sleep_time=0.01):
    """A slow function to test profiling."""
    time.sleep(sleep_time)
    return "result"


class TestCodeProfiler(unittest.TestCase):
    """Test suite for the CodeProfiler class."""

    def test_initialization(self):
        """Test that CodeProfiler initializes with correct values."""
        profiler = CodeProfiler(name="test_profile", sort_by="time")
        self.assertEqual(profiler.name, "test_profile")
        self.assertEqual(profiler.sort_by, "time")
        self.assertIsNone(profiler.results)

    def test_context_manager(self):
        """Test using CodeProfiler as a context manager."""
        with CodeProfiler(name="context_test") as profiler:
            slow_function(0.001)  # Very brief sleep to not slow down tests

        self.assertIsNotNone(profiler.results)
        self.assertEqual(profiler.name, "context_test")

    def test_decorator(self):
        """Test using CodeProfiler as a decorator."""

        # Define a decorated function
        @CodeProfiler(name="decorator_test")
        def decorated_func():
            slow_function(0.001)  # Very brief sleep
            return 42

        # Call the decorated function
        result = decorated_func()

        # Verify it executed correctly
        self.assertEqual(result, 42)

    def test_run_callable(self):
        """Test running and profiling a callable."""
        profiler = CodeProfiler(name="run_test")
        result = profiler.run(slow_function, 0.001)

        self.assertEqual(result, "result")
        self.assertIsNotNone(profiler.results)

    def test_run_code_string(self):
        """Test running and profiling a code string."""
        profiler = CodeProfiler(name="code_string_test")
        code = "x = 1 + 1"
        profiler.run(code)

        self.assertIsNotNone(profiler.results)

    def test_get_stats(self):
        """Test retrieving profiling statistics as a formatted string."""
        profiler = CodeProfiler(name="stats_test")
        with profiler:
            slow_function(0.001)  # Very brief sleep to not slow down tests

        stats = profiler.get_stats()
        self.assertIsInstance(stats, str)
        self.assertIn("function calls", stats)
        self.assertIn("slow_function", stats)

    def test_get_top_functions(self):
        """Test getting top functions by time consumption."""
        profiler = CodeProfiler(name="top_funcs_test")
        profiler.run(slow_function, 0.001)

        top_funcs = profiler.get_top_functions(limit=3)
        self.assertIsInstance(top_funcs, list)

        # Should have at least one function (slow_function)
        self.assertGreater(len(top_funcs), 0)

        # Verify structure of results
        if top_funcs:
            func = top_funcs[0]
            self.assertIn("function", func)
            self.assertIn("calls", func)
            self.assertIn("total_time", func)

    def test_identify_bottlenecks(self):
        """Test identifying performance bottlenecks."""
        profiler = CodeProfiler(name="bottleneck_test")

        # Profile a function that will definitely exceed our threshold
        profiler.run(slow_function, 0.01)

        # Set a low threshold to ensure we find bottlenecks
        bottlenecks = profiler.identify_bottlenecks(threshold_ms=1.0)

        # Verify structure of results
        self.assertIsInstance(bottlenecks, list)
        if bottlenecks:  # If any bottlenecks were found
            bottleneck = bottlenecks[0]
            self.assertIn("function", bottleneck)
            self.assertIn("is_bottleneck", bottleneck)
            self.assertTrue(bottleneck["is_bottleneck"])

    def test_profile_function_decorator(self):
        """Test the profile_function decorator."""

        # Define a decorated function
        @profile_function(name="profile_decorator_test", print_results=False)
        def test_func():
            slow_function(0.001)
            return "decorated_result"

        # Call the decorated function
        result = test_func()

        # Verify it executed correctly
        self.assertEqual(result, "decorated_result")

    @patch("tools.code_profiler.CodeProfiler")
    def test_profile_code_block(self, mock_profiler):
        """Test profiling a block of code as a string."""
        # Setup mock
        mock_instance = MagicMock()
        mock_profiler.return_value = mock_instance
        mock_instance.run.return_value = None
        mock_instance.identify_bottlenecks.return_value = []
        mock_instance.get_stats.return_value = "mock stats"
        mock_instance.get_top_functions.return_value = []

        # Profile a code block
        result = profile_code_block("x = 1 + 1", name="block_test")

        # Verify profiler was called correctly
        mock_profiler.assert_called_once_with(name="block_test")
        mock_instance.run.assert_called_once()

        # Verify result structure
        self.assertTrue(result["success"])
        self.assertIn("execution_time", result)
        self.assertIn("bottlenecks", result)
        self.assertIn("top_functions", result)
        self.assertIn("stats", result)

    @patch("tools.code_profiler.CodeProfiler.run")
    def test_profile_code_block_error(self, mock_run):
        """Test error handling in profile_code_block."""
        # Setup mock to raise an exception
        mock_run.side_effect = SyntaxError("Invalid syntax")

        # Profile a code block that will cause an error
        result = profile_code_block("invalid python code", name="error_test")

        # Verify error was handled
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("Invalid syntax", result["error"])

    def test_function_timer(self):
        """Test the FunctionTimer class."""
        # Test as context manager
        with FunctionTimer(name="timer_test") as timer:
            slow_function(0.001)

        self.assertGreater(timer.elapsed, 0)

        # Test as decorator
        @FunctionTimer(name="decorator_timer")
        def timed_function():
            slow_function(0.001)
            return 42

        result = timed_function()
        self.assertEqual(result, 42)


if __name__ == "__main__":
    unittest.main()
