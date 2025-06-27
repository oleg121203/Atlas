"""Response Time Optimization for Atlas (ASC-025)

This module implements strategies to reduce response times in the Atlas application as part of ASC-025. Techniques include asynchronous operations and caching.
"""

import asyncio
import logging
from functools import wraps

from PySide6.QtCore import QObject, QThread, Signal

# Setup logging
logger = logging.getLogger(__name__)


class AsyncTaskWorker(QObject):
    """A worker to run blocking tasks asynchronously in a separate thread."""

    taskCompleted = Signal(object, str)  # Result, Task ID
    taskError = Signal(str, str)  # Error message, Task ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._run_event_loop)
        self._tasks = {}
        self._loop = None
        logger.info("AsyncTaskWorker initialized")

    def start(self):
        """Start the worker thread with an asyncio event loop."""
        self.thread.start()
        logger.info("AsyncTaskWorker thread started")

    def _run_event_loop(self):
        """Run the asyncio event loop in this thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        logger.info("AsyncTaskWorker event loop started")

    def run_task(self, task_id: str, coro):
        """Run an asynchronous task in the worker thread.

        Args:
            task_id (str): Unique identifier for the task.
            coro: Coroutine to execute.
        """
        self._tasks[task_id] = coro
        asyncio.run_coroutine_threadsafe(self._execute_task(task_id), self._loop)
        logger.info(f"Scheduled async task: {task_id}")

    async def _execute_task(self, task_id: str):
        """Execute the task coroutine and emit results.

        Args:
            task_id (str): Unique identifier for the task.
        """
        try:
            coro = self._tasks.get(task_id)
            if coro:
                result = await coro
                self.taskCompleted.emit(result, task_id)
                logger.info(f"Async task completed: {task_id}")
            else:
                logger.warning(f"Task not found: {task_id}")
        except Exception as e:
            self.taskError.emit(str(e), task_id)
            logger.error(f"Error in async task {task_id}: {e}")
        finally:
            if task_id in self._tasks:
                del self._tasks[task_id]

    def stop(self):
        """Stop the worker thread and event loop."""
        if self._loop:
            self._loop.stop()
        self.thread.quit()
        self.thread.wait()
        logger.info("AsyncTaskWorker stopped")


class CacheManager:
    """Manages caching of frequently accessed data to improve response times."""

    def __init__(self, ttl_seconds=3600):
        self.ttl = ttl_seconds
        self._cache = {}
        logger.info(f"CacheManager initialized with TTL {ttl_seconds} seconds")

    def cached_function(self, func):
        """Decorator for caching function results."""
        # Використовуємо власний кеш замість lru_cache для уникнення витоків пам'яті
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Створюємо хешований ключ з аргументів
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
                # Перевіряємо розмір кешу і видаляємо старі записи при потребі
                if len(cache) > 128:
                    # Видаляємо перший (найстаріший) елемент
                    cache.pop(next(iter(cache)))
            return cache[key]

        logger.info(f"Applied cache to function {func.__name__}")
        return wrapper

    def get(self, key: str):
        """Get a value from the cache.

        Args:
            key (str): Cache key.

        Returns:
            object: Cached value if exists and not expired, None otherwise.
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            import time

            if time.time() - timestamp < self.ttl:
                logger.info(f"Cache hit for key: {key}")
                return value
            else:
                del self._cache[key]
                logger.info(f"Cache expired for key: {key}")
        return None

    def set(self, key: str, value):
        """Set a value in the cache with TTL.

        Args:
            key (str): Cache key.
            value: Value to cache.
        """
        import time

        self._cache[key] = (value, time.time())
        logger.info(f"Cache set for key: {key}")

    def clear(self, key: str = None):
        """Clear the cache or a specific key.

        Args:
            key (str, optional): Specific key to clear. If None, clears all.
        """
        if key is None:
            self._cache.clear()
            logger.info("Entire cache cleared")
        elif key in self._cache:
            del self._cache[key]
            logger.info(f"Cache cleared for key: {key}")
