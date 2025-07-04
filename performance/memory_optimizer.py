"""Memory Optimizer for Atlas

This module provides mechanisms to optimize memory usage throughout the application,
implementing memory management strategies like caching, lazy loading, and automatic
garbage collection to ensure efficient operation.
"""

import gc
import logging
import sys
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MemoryOptimizer:
    """Memory optimization system for Atlas components.

    Provides mechanisms to monitor and optimize memory usage throughout the application,
    implementing various memory management strategies like caching, lazy loading,
    and automatic garbage collection triggers.
    """

    def __init__(self, threshold_mb: int = 500, check_interval: int = 60):
        """Initialize the memory optimizer.

        Args:
            threshold_mb: Memory threshold in MB that triggers optimization
            check_interval: How often to check memory usage (in seconds)
        """
        self.threshold_mb = threshold_mb
        self.check_interval = check_interval
        self.last_check_time = 0
        self.optimization_count = 0
        self.monitoring_active = False
        self.cached_objects: Dict[str, Dict[str, Any]] = {}
        self.cache_stats: Dict[str, int] = {"hits": 0, "misses": 0}
        logger.info("MemoryOptimizer initialized with threshold: %d MB", threshold_mb)

    def start_monitoring(self):
        """Start the memory monitoring process."""
        self.monitoring_active = True
        self.last_check_time = time.time()
        logger.info("Memory optimization monitoring started")

    def stop_monitoring(self):
        """Stop the memory monitoring process."""
        self.monitoring_active = False
        logger.info("Memory optimization monitoring stopped")

    def check_memory_usage(self) -> Dict[str, Any]:
        """Check current memory usage and trigger optimization if needed.

        Returns:
            Dict containing memory usage information
        """
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            # Not time to check yet
            return {}

        self.last_check_time = current_time

        # Get current memory usage
        memory_info = self.get_memory_info()
        current_usage_mb = memory_info["used_mb"]

        # If memory usage exceeds threshold, optimize
        if current_usage_mb > self.threshold_mb:
            logger.warning(
                "Memory usage (%d MB) exceeds threshold (%d MB), optimizing",
                current_usage_mb,
                self.threshold_mb,
            )
            self.optimize_memory()

            # Get updated memory usage after optimization
            memory_info = self.get_memory_info()
            logger.info(
                "After optimization: %d MB used (saved: %d MB)",
                memory_info["used_mb"],
                current_usage_mb - memory_info["used_mb"],
            )

        return memory_info

    def get_memory_info(self) -> Dict[str, float]:
        """Get detailed memory usage information.

        Returns:
            Dict containing memory usage metrics in MB
        """
        usage = {}

        # Get memory usage from Python's system info
        usage["used_mb"] = sys.getsizeof(0)
        for obj in gc.get_objects():
            try:
                usage["used_mb"] += sys.getsizeof(obj)
            except (TypeError, AttributeError):
                # Some objects can't be sized
                pass

        # Convert to MB
        usage["used_mb"] = usage["used_mb"] / (1024 * 1024)

        return usage

    def optimize_memory(self) -> bool:
        """Perform memory optimization operations.

        Returns:
            True if optimization was successful, False otherwise
        """
        try:
            # Run garbage collection
            collected = gc.collect()
            logger.info("Garbage collection: %d objects collected", collected)

            # Clear unused caches
            cleared_items = self._clear_expired_cache_items()
            logger.info("Cache cleanup: %d items removed", cleared_items)

            self.optimization_count += 1
            return True
        except Exception as e:
            logger.error("Memory optimization failed: %s", str(e))
            return False

    def cache_object(self, category: str, key: str, obj: Any, ttl_seconds: int = 300):
        """Cache an object for later retrieval.

        Args:
            category: Category for grouping related cached objects
            key: Unique identifier for the object
            obj: The object to cache
            ttl_seconds: Time to live in seconds before cache expiration
        """
        if category not in self.cached_objects:
            self.cached_objects[category] = {}

        self.cached_objects[category][key] = {
            "object": obj,
            "expires_at": time.time() + ttl_seconds,
        }

        logger.debug(
            "Object cached: %s/%s (expires in %d seconds)", category, key, ttl_seconds
        )

    def get_cached_object(self, category: str, key: str) -> Optional[Any]:
        """Retrieve an object from cache.

        Args:
            category: Category the object was cached under
            key: Unique identifier for the object

        Returns:
            The cached object if found and not expired, None otherwise
        """
        if (
            category not in self.cached_objects
            or key not in self.cached_objects[category]
        ):
            self.cache_stats["misses"] += 1
            return None

        cache_item = self.cached_objects[category][key]

        # Check if expired
        if cache_item["expires_at"] < time.time():
            # Remove expired item
            del self.cached_objects[category][key]
            self.cache_stats["misses"] += 1
            return None

        self.cache_stats["hits"] += 1
        return cache_item["object"]

    def clear_cache(self, category: str = None) -> None:
        """Clear cached objects, optionally for a specific category."""
        if category is None:
            self.cached_objects.clear()
            logger.debug("All cached objects cleared")
        else:
            if category in self.cached_objects:
                del self.cached_objects[category]
                logger.debug(f"Cached objects cleared for category: {category}")
            else:
                logger.warning(f"Category {category} not found in cache")

    def _clear_expired_cache_items(self) -> int:
        """Remove all expired items from cache.

        Returns:
            Number of items removed
        """
        current_time = time.time()
        removed_count = 0

        for category in list(self.cached_objects.keys()):
            for key in list(self.cached_objects[category].keys()):
                if self.cached_objects[category][key]["expires_at"] < current_time:
                    del self.cached_objects[category][key]
                    removed_count += 1

            # If category is empty, remove it
            if not self.cached_objects[category]:
                del self.cached_objects[category]

        return removed_count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about cache usage.

        Returns:
            Dict containing cache statistics
        """
        stats = self.cache_stats.copy()

        # Calculate hit ratio
        total_requests = stats["hits"] + stats["misses"]
        stats["hit_ratio"] = stats["hits"] / total_requests if total_requests > 0 else 0

        # Add category information
        stats["categories"] = {}
        for category, items in self.cached_objects.items():
            stats["categories"][category] = len(items)

        return stats

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get statistics about optimization operations.

        Returns:
            Dict containing optimization statistics
        """
        return {
            "optimization_count": self.optimization_count,
            "threshold_mb": self.threshold_mb,
            "check_interval": self.check_interval,
            "last_check_time": self.last_check_time,
            "monitoring_active": self.monitoring_active,
        }


# Singleton instance
_memory_optimizer: Optional[MemoryOptimizer] = None


def get_memory_optimizer() -> MemoryOptimizer:
    """Get the singleton MemoryOptimizer instance.

    Returns:
        The global MemoryOptimizer instance
    """
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer


def optimize_memory():
    """Convenience function to trigger memory optimization."""
    optimizer = get_memory_optimizer()
    return optimizer.optimize_memory()


def cache_object(category: str, key: str, obj: Any, ttl_seconds: int = 300):
    """Convenience function to cache an object."""
    optimizer = get_memory_optimizer()
    optimizer.cache_object(category, key, obj, ttl_seconds)


def get_cached_object(category: str, key: str) -> Optional[Any]:
    """Convenience function to retrieve a cached object."""
    optimizer = get_memory_optimizer()
    return optimizer.get_cached_object(category, key)
