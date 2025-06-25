"""
Cache Manager for Atlas using Redis.
This module provides a simple interface for caching frequently accessed data to improve performance.
"""

import json
from typing import Any, Optional
import redis.asyncio as redis

class CacheManager:
    """
    A class to manage caching operations using Redis for Atlas application.
    """
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        """
        Initialize the CacheManager with Redis connection parameters.
        
        Args:
            host (str): Redis server host.
            port (int): Redis server port.
            db (int): Redis database number.
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.connected = False

    async def connect(self) -> None:
        """
        Establish connection to Redis server.
        """
        try:
            await self.client.ping()
            self.connected = True
            print("Connected to Redis successfully.")
        except redis.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
            self.connected = False

    async def close(self) -> None:
        """
        Close connection to Redis server.
        """
        if self.connected:
            await self.client.close()
            self.connected = False
            print("Redis connection closed.")

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache with an optional time-to-live (TTL).
        
        Args:
            key (str): Cache key.
            value (Any): Value to cache. If not a string, will be JSON serialized.
            ttl (int, optional): Time to live in seconds. If None, persists indefinitely.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.connected:
            await self.connect()
        if not self.connected:
            return False

        try:
            if not isinstance(value, str):
                value = json.dumps(value)
            await self.client.set(key, value)
            if ttl is not None:
                await self.client.expire(key, ttl)
            return True
        except redis.RedisError as e:
            print(f"Error setting cache value: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache.
        
        Args:
            key (str): Cache key to lookup.
        
        Returns:
            Any: Cached value if found, None otherwise. Attempts JSON deserialization if applicable.
        """
        if not self.connected:
            await self.connect()
        if not self.connected:
            return None

        try:
            value = await self.client.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except redis.RedisError as e:
            print(f"Error getting cache value: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key (str): Cache key to delete.
        
        Returns:
            bool: True if key was deleted or didn't exist, False on error.
        """
        if not self.connected:
            await self.connect()
        if not self.connected:
            return False

        try:
            await self.client.delete(key)
            return True
        except redis.RedisError as e:
            print(f"Error deleting cache key: {e}")
            return False

# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        cache = CacheManager()
        await cache.connect()
        
        # Set a simple string value with 60 seconds TTL
        await cache.set("user:1:last_seen", "2023-10-05T10:00:00Z", ttl=60)
        # Set a complex object
        user_data = {"id": 1, "name": "John Doe", "tasks": [1, 2, 3]}
        await cache.set("user:1:data", user_data, ttl=300)
        
        # Retrieve values
        last_seen = await cache.get("user:1:last_seen")
        user_info = await cache.get("user:1:data")
        print(f"Last Seen: {last_seen}")
        print(f"User Info: {user_info}")
        
        # Clean up
        await cache.close()

    asyncio.run(main())
