"""
Tests for the CacheManager module.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utils.cache_manager import CacheManager


@pytest.mark.asyncio
class TestCacheManager:
    """Test cases for the CacheManager class."""

    @patch("redis.asyncio.Redis")
    async def test_connect_success(self, mock_redis):
        """Test successful connection to Redis."""
        # Setup
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()

        # Assert
        assert cache_manager.connected is True
        redis_instance.ping.assert_called_once()

    @patch("redis.asyncio.Redis")
    async def test_connect_failure(self, mock_redis):
        """Test connection failure to Redis."""
        # Setup
        import redis.asyncio as redis

        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(
            side_effect=redis.ConnectionError("Connection refused")
        )

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()

        # Assert
        assert cache_manager.connected is False
        redis_instance.ping.assert_called_once()

    @patch("redis.asyncio.Redis")
    async def test_close(self, mock_redis):
        """Test closing Redis connection."""
        # Setup
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)
        redis_instance.close = AsyncMock()

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()
        await cache_manager.close()

        # Assert
        assert cache_manager.connected is False
        redis_instance.close.assert_called_once()

    @patch("redis.asyncio.Redis")
    async def test_set_string_value(self, mock_redis):
        """Test setting a string value in cache."""
        # Setup
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)
        redis_instance.set = AsyncMock(return_value=True)

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()
        result = await cache_manager.set("test_key", "test_value")

        # Assert
        assert result is True
        redis_instance.set.assert_called_once_with("test_key", "test_value")

    @patch("redis.asyncio.Redis")
    async def test_set_dict_value(self, mock_redis):
        """Test setting a dictionary value in cache."""
        # Setup
        test_dict = {"name": "Test", "value": 123}
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)
        redis_instance.set = AsyncMock(return_value=True)

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()
        result = await cache_manager.set("test_key", test_dict)

        # Assert
        assert result is True
        redis_instance.set.assert_called_once_with("test_key", json.dumps(test_dict))

    @patch("redis.asyncio.Redis")
    async def test_set_with_ttl(self, mock_redis):
        """Test setting a value with TTL in cache."""
        # Setup
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)
        redis_instance.set = AsyncMock(return_value=True)
        redis_instance.expire = AsyncMock(return_value=True)

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()
        result = await cache_manager.set("test_key", "test_value", ttl=100)

        # Assert
        assert result is True
        redis_instance.set.assert_called_once_with("test_key", "test_value")
        redis_instance.expire.assert_called_once_with("test_key", 100)

    @patch("redis.asyncio.Redis")
    async def test_set_without_connection(self, mock_redis):
        """Test setting a value when not connected."""
        # Setup
        import redis.asyncio as redis

        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(
            side_effect=redis.ConnectionError("Connection refused")
        )

        # Execute
        cache_manager = CacheManager()
        result = await cache_manager.set("test_key", "test_value")

        # Assert
        assert result is False

    @patch("redis.asyncio.Redis")
    async def test_get_existing_value(self, mock_redis):
        """Test getting an existing value from cache."""
        # Setup
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)
        redis_instance.get = AsyncMock(return_value="test_value")

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()
        result = await cache_manager.get("test_key")

        # Assert
        assert result == "test_value"
        redis_instance.get.assert_called_once_with("test_key")

    @patch("redis.asyncio.Redis")
    async def test_get_json_value(self, mock_redis):
        """Test getting a JSON value from cache."""
        # Setup
        test_dict = {"name": "Test", "value": 123}
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)
        redis_instance.get = AsyncMock(return_value=json.dumps(test_dict))

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()
        result = await cache_manager.get("test_key")

        # Assert
        assert result == test_dict
        redis_instance.get.assert_called_once_with("test_key")

    @patch("redis.asyncio.Redis")
    async def test_get_nonexistent_value(self, mock_redis):
        """Test getting a non-existent value from cache."""
        # Setup
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)
        redis_instance.get = AsyncMock(return_value=None)

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()
        result = await cache_manager.get("nonexistent_key")

        # Assert
        assert result is None
        redis_instance.get.assert_called_once_with("nonexistent_key")

    @patch("redis.asyncio.Redis")
    async def test_delete_key(self, mock_redis):
        """Test deleting a key from cache."""
        # Setup
        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(return_value=True)
        redis_instance.delete = AsyncMock(return_value=1)

        # Execute
        cache_manager = CacheManager()
        await cache_manager.connect()
        result = await cache_manager.delete("test_key")

        # Assert
        assert result is True
        redis_instance.delete.assert_called_once_with("test_key")

    @patch("redis.asyncio.Redis")
    async def test_delete_without_connection(self, mock_redis):
        """Test deleting a key when not connected."""
        # Setup
        import redis.asyncio as redis

        redis_instance = mock_redis.return_value
        redis_instance.ping = AsyncMock(
            side_effect=redis.ConnectionError("Connection refused")
        )

        # Execute
        cache_manager = CacheManager()
        result = await cache_manager.delete("test_key")

        # Assert
        assert result is False
