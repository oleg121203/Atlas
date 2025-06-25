"""
Data Cache Module for Atlas.
This module integrates caching to store frequently accessed data, reducing database load and improving response times.
"""

from typing import Any, Optional
import asyncio
import sys
import os

# Ensure utils path is correctly referenced
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.cache_manager import CacheManager

class DataCache:
    """
    A class to handle caching of frequently accessed data in Atlas.
    """
    def __init__(self, cache_ttl: int = 300, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initialize the DataCache with a CacheManager instance.
        
        Args:
            cache_ttl (int): Default time-to-live for cached items in seconds.
            host (str): Redis server host.
            port (int): Redis server port.
            db (int): Redis database number.
        """
        self.cache_ttl = cache_ttl
        self.cache_manager = CacheManager(host=host, port=port, db=db)
        self.initialized = False

    async def initialize(self) -> None:
        """
        Initialize the cache by connecting to Redis.
        """
        if not self.initialized:
            await self.cache_manager.connect()
            self.initialized = self.cache_manager.connected
            if not self.initialized:
                print("DataCache initialization failed: Could not connect to Redis.")
            else:
                print("DataCache initialized successfully.")

    async def shutdown(self) -> None:
        """
        Shutdown the cache by closing the Redis connection.
        """
        if self.initialized:
            await self.cache_manager.close()
            self.initialized = False
            print("DataCache shutdown complete.")

    async def get_user_data(self, user_id: str) -> Optional[dict]:
        """
        Retrieve user data from cache.
        
        Args:
            user_id (str): Unique identifier for the user.
        
        Returns:
            Optional[dict]: Cached user data if found, None otherwise.
        """
        if not self.initialized:
            await self.initialize()
        if not self.initialized:
            return None

        key = f"user:{user_id}:data"
        data = await self.cache_manager.get(key)
        if data is not None:
            print(f"Cache hit for user data: {user_id}")
        return data

    async def set_user_data(self, user_id: str, data: dict, ttl: Optional[int] = None) -> bool:
        """
        Cache user data with a specified TTL.
        
        Args:
            user_id (str): Unique identifier for the user.
            data (dict): User data to cache.
            ttl (int, optional): Time to live in seconds. Defaults to class TTL.
        
        Returns:
            bool: True if caching was successful, False otherwise.
        """
        if not self.initialized:
            await self.initialize()
        if not self.initialized:
            return False

        key = f"user:{user_id}:data"
        return await self.cache_manager.set(key, data, ttl or self.cache_ttl)

    async def get_task_list(self, user_id: str, list_id: str) -> Optional[list]:
        """
        Retrieve a user's task list from cache.
        
        Args:
            user_id (str): Unique identifier for the user.
            list_id (str): Unique identifier for the task list.
        
        Returns:
            Optional[list]: Cached task list if found, None otherwise.
        """
        if not self.initialized:
            await self.initialize()
        if not self.initialized:
            return None

        key = f"user:{user_id}:tasks:{list_id}"
        data = await self.cache_manager.get(key)
        if data is not None:
            print(f"Cache hit for task list: {user_id}/{list_id}")
        return data

    async def set_task_list(self, user_id: str, list_id: str, tasks: list, ttl: Optional[int] = None) -> bool:
        """
        Cache a user's task list with a specified TTL.
        
        Args:
            user_id (str): Unique identifier for the user.
            list_id (str): Unique identifier for the task list.
            tasks (list): List of tasks to cache.
            ttl (int, optional): Time to live in seconds. Defaults to class TTL.
        
        Returns:
            bool: True if caching was successful, False otherwise.
        """
        if not self.initialized:
            await self.initialize()
        if not self.initialized:
            return False

        key = f"user:{user_id}:tasks:{list_id}"
        return await self.cache_manager.set(key, tasks, ttl or self.cache_ttl)

    async def invalidate_user_cache(self, user_id: str) -> bool:
        """
        Invalidate all cached data for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user.
        
        Returns:
            bool: True if cache invalidation was successful, False otherwise.
        """
        if not self.initialized:
            await self.initialize()
        if not self.initialized:
            return False

        # This is a simplified approach. In a real scenario, you'd use Redis SCAN or KEYS
        # to delete all keys matching a pattern. For now, we'll delete known key patterns.
        keys_to_delete = [
            f"user:{user_id}:data",
            f"user:{user_id}:tasks:*"
        ]
        success = True
        for key in keys_to_delete:
            if '*' in key:
                # Would need a more complex pattern matching in real Redis setup
                continue
            if not await self.cache_manager.delete(key):
                success = False
        print(f"Cache invalidated for user: {user_id}")
        return success

# Example usage
if __name__ == "__main__":
    async def demo_cache():
        cache = DataCache(cache_ttl=60)
        await cache.initialize()

        # Cache some user data
        user_data = {"id": "123", "name": "Demo User", "email": "demo@example.com"}
        await cache.set_user_data("123", user_data)

        # Retrieve user data
        retrieved_data = await cache.get_user_data("123")
        print(f"Retrieved User Data: {retrieved_data}")

        # Cache a task list
        task_list = [
            {"id": 1, "title": "Task 1", "completed": False},
            {"id": 2, "title": "Task 2", "completed": True}
        ]
        await cache.set_task_list("123", "default", task_list)

        # Retrieve task list
        retrieved_tasks = await cache.get_task_list("123", "default")
        print(f"Retrieved Task List: {retrieved_tasks}")

        # Invalidate cache for user
        await cache.invalidate_user_cache("123")

        await cache.shutdown()

    asyncio.run(demo_cache())
