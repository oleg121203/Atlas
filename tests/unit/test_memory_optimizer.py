"""Unit tests for the MemoryOptimizer class.

Tests functionality of the memory optimizer including caching, memory monitoring,
and optimization operations.
"""

import time
import unittest
from unittest.mock import patch

from performance.memory_optimizer import (
    MemoryOptimizer,
    cache_object,
    get_cached_object,
    get_memory_optimizer,
    optimize_memory,
)


class TestMemoryOptimizer(unittest.TestCase):
    """Test suite for the MemoryOptimizer class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a fresh instance for each test
        self.optimizer = MemoryOptimizer(threshold_mb=100, check_interval=10)

    def test_initialization(self):
        """Test that MemoryOptimizer initializes with correct values."""
        self.assertEqual(self.optimizer.threshold_mb, 100)
        self.assertEqual(self.optimizer.check_interval, 10)
        self.assertEqual(self.optimizer.optimization_count, 0)
        self.assertFalse(self.optimizer.monitoring_active)
        self.assertEqual(self.optimizer.cached_objects, {})
        self.assertEqual(self.optimizer.cache_stats, {"hits": 0, "misses": 0})

    def test_start_stop_monitoring(self):
        """Test starting and stopping memory monitoring."""
        self.assertFalse(self.optimizer.monitoring_active)

        self.optimizer.start_monitoring()
        self.assertTrue(self.optimizer.monitoring_active)
        self.assertGreater(self.optimizer.last_check_time, 0)

        self.optimizer.stop_monitoring()
        self.assertFalse(self.optimizer.monitoring_active)

    @patch("performance.memory_optimizer.MemoryOptimizer.get_memory_info")
    @patch("performance.memory_optimizer.MemoryOptimizer.optimize_memory")
    def test_check_memory_usage_below_threshold(self, mock_optimize, mock_get_info):
        """Test memory checking when usage is below threshold."""
        # Set up mock to return memory usage below threshold
        mock_get_info.return_value = {"used_mb": 50}

        # Set last check time far in the past to ensure check runs
        self.optimizer.last_check_time = 0

        result = self.optimizer.check_memory_usage()

        # Verify memory info was retrieved
        mock_get_info.assert_called_once()

        # Verify optimization was not triggered
        mock_optimize.assert_not_called()

        # Verify correct result
        self.assertEqual(result, {"used_mb": 50})

    @patch("performance.memory_optimizer.MemoryOptimizer.get_memory_info")
    @patch("performance.memory_optimizer.MemoryOptimizer.optimize_memory")
    def test_check_memory_usage_above_threshold(self, mock_optimize, mock_get_info):
        """Test memory checking when usage is above threshold."""
        # First call (before optimization) returns high memory usage
        # Second call (after optimization) returns lower memory usage
        mock_get_info.side_effect = [{"used_mb": 150}, {"used_mb": 80}]
        mock_optimize.return_value = True

        # Set last check time far in the past to ensure check runs
        self.optimizer.last_check_time = 0

        result = self.optimizer.check_memory_usage()

        # Verify memory info was retrieved twice (before and after optimization)
        self.assertEqual(mock_get_info.call_count, 2)

        # Verify optimization was triggered
        mock_optimize.assert_called_once()

        # Verify correct result (the post-optimization value)
        self.assertEqual(result, {"used_mb": 80})

    def test_check_memory_usage_too_soon(self):
        """Test that memory checking respects the check interval."""
        # Set last check time to current time
        self.optimizer.last_check_time = time.time()

        with patch(
            "performance.memory_optimizer.MemoryOptimizer.get_memory_info"
        ) as mock_get_info:
            result = self.optimizer.check_memory_usage()

            # Verify memory info was not retrieved
            mock_get_info.assert_not_called()

            # Verify empty result
            self.assertEqual(result, {})

    @patch("gc.collect")
    def test_optimize_memory(self, mock_collect):
        """Test memory optimization operations."""
        mock_collect.return_value = 42  # 42 objects collected

        # Add some expired cache items to test cleanup
        self.optimizer.cached_objects = {
            "test": {
                "item1": {
                    "object": "value1",
                    "expires_at": time.time() - 100,
                },  # expired
                "item2": {
                    "object": "value2",
                    "expires_at": time.time() + 100,
                },  # not expired
            }
        }

        result = self.optimizer.optimize_memory()

        # Verify garbage collection was called
        mock_collect.assert_called_once()

        # Verify expired cache items were cleared
        self.assertNotIn("item1", self.optimizer.cached_objects["test"])
        self.assertIn("item2", self.optimizer.cached_objects["test"])

        # Verify optimization count was incremented
        self.assertEqual(self.optimizer.optimization_count, 1)

        # Verify success result
        self.assertTrue(result)

    def test_cache_object_and_retrieval(self):
        """Test caching objects and retrieving them."""
        # Cache a test object
        test_obj = {"data": "test_value"}
        self.optimizer.cache_object("category1", "key1", test_obj, ttl_seconds=60)

        # Verify it was cached properly
        self.assertIn("category1", self.optimizer.cached_objects)
        self.assertIn("key1", self.optimizer.cached_objects["category1"])

        # Retrieve it and verify it matches
        retrieved = self.optimizer.get_cached_object("category1", "key1")
        self.assertEqual(retrieved, test_obj)

        # Verify hit was recorded
        self.assertEqual(self.optimizer.cache_stats["hits"], 1)
        self.assertEqual(self.optimizer.cache_stats["misses"], 0)

    def test_cache_expired_object(self):
        """Test retrieving an expired cached object."""
        # Cache a test object with a very short TTL
        test_obj = {"data": "test_value"}
        self.optimizer.cache_object("category1", "key1", test_obj, ttl_seconds=0.01)

        # Wait for it to expire
        time.sleep(0.02)

        # Try to retrieve it
        retrieved = self.optimizer.get_cached_object("category1", "key1")

        # Verify it's not returned and a miss was recorded
        self.assertIsNone(retrieved)
        self.assertEqual(self.optimizer.cache_stats["hits"], 0)
        self.assertEqual(self.optimizer.cache_stats["misses"], 1)

        # Verify it was removed from cache
        self.assertNotIn("key1", self.optimizer.cached_objects.get("category1", {}))

    def test_cache_missing_object(self):
        """Test retrieving a non-existent cached object."""
        # Try to retrieve an object that wasn't cached
        retrieved = self.optimizer.get_cached_object("nonexistent", "missing")

        # Verify it's not returned and a miss was recorded
        self.assertIsNone(retrieved)
        self.assertEqual(self.optimizer.cache_stats["hits"], 0)
        self.assertEqual(self.optimizer.cache_stats["misses"], 1)

    def test_clear_cache_specific_category(self):
        """Test clearing cache for a specific category."""
        self.optimizer.cached_objects = {
            "category1": {
                "key1": {"object": "value1", "expires_at": time.time() + 100}
            },
            "category2": {
                "key2": {"object": "value2", "expires_at": time.time() + 100}
            },
        }
        self.optimizer.clear_cache(category="category1")
        self.assertNotIn("category1", self.optimizer.cached_objects)
        self.assertIn("category2", self.optimizer.cached_objects)

    def test_clear_all_cache(self):
        """Test clearing the entire cache."""
        # Cache objects in different categories
        self.optimizer.cache_object("category1", "key1", "value1")
        self.optimizer.cache_object("category2", "key2", "value2")

        # Clear all cache
        self.optimizer.clear_cache()

        # Verify all categories are cleared
        self.assertEqual(self.optimizer.cached_objects, {})

    def test_get_cache_stats(self):
        """Test retrieving cache statistics."""
        # Setup some cache hits and misses
        self.optimizer.cache_object("category1", "key1", "value1")
        self.optimizer.get_cached_object("category1", "key1")  # hit
        self.optimizer.get_cached_object("missing", "key")  # miss

        # Get stats
        stats = self.optimizer.get_cache_stats()

        # Verify stats are correct
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hit_ratio"], 0.5)  # 1 hit / 2 requests
        self.assertEqual(stats["categories"], {"category1": 1})

    def test_get_optimization_stats(self):
        """Test retrieving optimization statistics."""
        # Setup some optimization activity
        self.optimizer.optimization_count = 3
        self.optimizer.start_monitoring()

        # Get stats
        stats = self.optimizer.get_optimization_stats()

        # Verify stats are correct
        self.assertEqual(stats["optimization_count"], 3)
        self.assertEqual(stats["threshold_mb"], 100)
        self.assertEqual(stats["check_interval"], 10)
        self.assertTrue(stats["monitoring_active"])

    def test_singleton_functions(self):
        """Test the singleton access functions."""
        with patch("performance.memory_optimizer._memory_optimizer", None):
            # First call should create the optimizer
            optimizer1 = get_memory_optimizer()
            self.assertIsInstance(optimizer1, MemoryOptimizer)

            # Second call should return the same instance
            optimizer2 = get_memory_optimizer()
            self.assertIs(optimizer1, optimizer2)

            # Test convenience functions
            with patch.object(optimizer1, "optimize_memory") as mock_optimize:
                optimize_memory()
                mock_optimize.assert_called_once()

            with patch.object(optimizer1, "cache_object") as mock_cache:
                cache_object("cat", "key", "value", 100)
                mock_cache.assert_called_once_with("cat", "key", "value", 100)

            with patch.object(optimizer1, "get_cached_object") as mock_get:
                mock_get.return_value = "cached_value"
                result = get_cached_object("cat", "key")
                mock_get.assert_called_once_with("cat", "key")
                self.assertEqual(result, "cached_value")


if __name__ == "__main__":
    unittest.main()
