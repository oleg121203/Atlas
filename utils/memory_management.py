"""Memory Management Utilities for Atlas Application.

This module provides tools and strategies for efficient memory management,
including caching, cleanup, and monitoring of memory usage to handle large
datasets and long-running operations.
"""

import gc
import logging
import os
import threading
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import psutil

# Setup logging
logger = logging.getLogger(__name__)


class MemoryManager:
    """A class to manage memory operations for Atlas, including caching and interaction storage."""

    def __init__(
        self,
        cache_size_limit: int = 1000,
        ttl_seconds: int = 3600,
        cleanup_interval: int = 300,
    ):
        """Initialize the MemoryManager with specified limits and intervals.

        Args:
            cache_size_limit (int): Maximum number of items to store in the cache.
            ttl_seconds (int): Time-to-live for cache items in seconds.
            cleanup_interval (int): Interval in seconds between automatic cleanup operations.
        """
        self.cache_size_limit = cache_size_limit
        self.ttl_seconds = ttl_seconds
        self.cleanup_interval = cleanup_interval
        self.cache: Dict[str, Tuple[Any, float]] = {}  # Tuple of (value, timestamp)
        self.interactions: Dict[str, List[Dict[str, Any]]] = defaultdict(
            list
        )  # User interactions storage
        self.feedback: Dict[str, List[Dict[str, Any]]] = defaultdict(
            list
        )  # User feedback storage
        self._lock = threading.Lock()
        logger.info(
            "MemoryManager initialized with cache size limit %d and TTL %d seconds",
            cache_size_limit,
            ttl_seconds,
        )

    def get_memory_usage(self) -> float:
        """Get current memory usage of the application in megabytes.

        Returns:
            float: Memory usage in MB.
        """
        mem_info = psutil.Process(os.getpid()).memory_info()
        usage_mb = mem_info.rss / 1024 / 1024  # Convert bytes to MB
        logger.debug("Current memory usage: %.2f MB", usage_mb)
        return usage_mb

    def add_to_cache(
        self, key: str, value: Any, size_estimate: Optional[int] = None
    ) -> bool:
        """Add an item to the cache with expiration.

        Args:
            key: Unique key for the cache item.
            value: The value to cache.
            size_estimate: Estimated size of the value in bytes. If None, a rough estimate is used.

        Returns:
            bool: True if added to cache, False if not added due to size constraints.
        """
        # Estimate size if not provided (rough approximation)
        if size_estimate is None:
            size_estimate = self._estimate_size(value)

        # Check if adding this item would exceed cache size limit
        if len(self.cache) + 1 > self.cache_size_limit:
            logger.warning("Cache size limit reached, evicting old items")
            self._evict_cache()
            if len(self.cache) + 1 > self.cache_size_limit:
                logger.error("Item too large for cache, not added: %s", key)
                return False

        # Add to cache with timestamp
        with self._lock:
            self.cache[key] = (value, time.time())
        logger.debug(
            "Added to cache: %s, size: %d bytes, total cache size: %d items",
            key,
            size_estimate,
            len(self.cache),
        )
        return True

    def get_from_cache(self, key: str) -> Optional[Any]:
        """Retrieve an item from the cache if it exists and is not expired.

        Args:
            key: Unique key for the cache item.

        Returns:
            Optional[Any]: Cached value if found and not expired, None otherwise.
        """
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    logger.debug("Cache hit for key: %s", key)
                    return value
                else:
                    del self.cache[key]
                    logger.debug("Cache expired for key: %s", key)
        return None

    def clear_cache(self) -> None:
        """Clear all items from the cache."""
        with self._lock:
            self.cache.clear()
        logger.info("Cache cleared")

    def _evict_cache(self) -> None:
        """Evict items from cache based on expiration and age to make space."""
        # First, remove expired items
        with self._lock:
            expired_keys = []
            for key, (_, timestamp) in self.cache.items():
                if time.time() - timestamp >= self.ttl_seconds:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]
                logger.debug("Evicted expired item from cache: %s", key)

            # If still not enough space, remove oldest items
            if len(self.cache) > self.cache_size_limit:
                sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
                for key, _ in sorted_items:
                    if len(self.cache) <= self.cache_size_limit:
                        break
                    del self.cache[key]
                    logger.debug("Evicted old item from cache to make space: %s", key)

    def _estimate_size(self, obj: Any) -> int:
        """Roughly estimate the size of an object in bytes.

        Args:
            obj: Object to estimate size for.

        Returns:
            int: Estimated size in bytes.
        """
        # This is a very rough estimation and might need to be improved
        # based on specific data types used in Atlas
        try:
            import sys

            return sys.getsizeof(obj)
        except Exception as e:
            logger.warning("Could not estimate size for object: %s", e)
            return 0

    def store_interaction(
        self,
        user_id: str,
        query: str,
        response: str,
        rating: Optional[float] = None,
        timestamp: str = None,
    ) -> None:
        """Store a user interaction for future learning and reference.

        Args:
            user_id (str): Unique identifier for the user.
            query (str): The user's query or input.
            response (str): The AI's response to the query.
            rating (float, optional): User rating of the response. Defaults to None.
            timestamp (str, optional): ISO format timestamp of the interaction. Defaults to None (current time).
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        interaction = {
            "query": query,
            "response": response,
            "rating": rating,
            "timestamp": timestamp,
        }
        with self._lock:
            self.interactions[user_id].append(interaction)
            # Limit to last 100 interactions per user to manage memory
            if len(self.interactions[user_id]) > 100:
                self.interactions[user_id] = self.interactions[user_id][-100:]
        logger.debug(f"Stored interaction for user {user_id} at {timestamp}")

    def store_feedback(
        self, user_id: str, response_id: str, rating: float, timestamp: str = None
    ) -> None:
        """Store user feedback for a specific response.

        Args:
            user_id (str): Unique identifier for the user.
            response_id (str): Unique identifier for the response being rated.
            rating (float): User rating of the response (e.g., 1-5).
            timestamp (str, optional): ISO format timestamp of the feedback. Defaults to None (current time).
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        feedback = {
            "response_id": response_id,
            "rating": rating,
            "timestamp": timestamp,
        }
        with self._lock:
            self.feedback[user_id].append(feedback)
            # Limit to last 100 feedback entries per user to manage memory
            if len(self.feedback[user_id]) > 100:
                self.feedback[user_id] = self.feedback[user_id][-100:]
        logger.debug(
            f"Stored feedback for user {user_id} on response {response_id} with rating {rating}"
        )

    def get_user_interactions(
        self, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve a user's interaction history.

        Args:
            user_id (str): Unique identifier for the user.
            limit (int): Maximum number of interactions to return. Defaults to 50.

        Returns:
            List[Dict[str, Any]]: List of interaction dictionaries.
        """
        with self._lock:
            interactions = self.interactions.get(user_id, [])[-limit:]
        logger.debug(f"Retrieved {len(interactions)} interactions for user {user_id}")
        return interactions

    def get_user_feedback(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve a user's feedback history.

        Args:
            user_id (str): Unique identifier for the user.
            limit (int): Maximum number of feedback entries to return. Defaults to 50.

        Returns:
            List[Dict[str, Any]]: List of feedback dictionaries.
        """
        with self._lock:
            feedback = self.feedback.get(user_id, [])[-limit:]
        logger.debug(f"Retrieved {len(feedback)} feedback entries for user {user_id}")
        return feedback

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the memory cache by key.

        Args:
            key (str): The key to look up.

        Returns:
            Optional[Any]: The value if found and not expired, None otherwise.
        """
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    logger.debug(f"Cache hit for key: {key}")
                    return value
                else:
                    del self.cache[key]
                    logger.debug(f"Cache expired for key: {key}")
            return None

    def perform_cleanup(self) -> None:
        """Perform general memory cleanup, including garbage collection and cache eviction."""
        # Clear expired cache items
        self._evict_cache()
        # Force garbage collection
        gc.collect()
        logger.info(
            "Memory cleanup performed, current usage: %.2f MB", self.get_memory_usage()
        )

    def log_memory_stats(self) -> None:
        """Log detailed memory usage statistics for debugging."""
        mem_usage = self.get_memory_usage()
        cache_items = len(self.cache)
        cache_size_mb = self.cache_size_limit / 1024 / 1024
        logger.info(
            "Memory Stats: Usage=%.2f MB, Cache Items=%d, Cache Size=%.2f MB",
            mem_usage,
            cache_items,
            cache_size_mb,
        )


# Singleton instance for global memory management
MEMORY_MANAGER = MemoryManager()
