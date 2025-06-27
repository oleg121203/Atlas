"""
Tests for the DataCache module.
"""

import asyncio
import unittest.mock
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from core.data_cache import DataCache


@pytest.mark.asyncio
class TestDataCache:
    """Test cases for the DataCache class."""

    async def test_initialize(self):
        """Test cache initialization succeeds."""
        # Setup
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.connected = True

            # Execute
            cache = DataCache(cache_ttl=60)
            await cache.initialize()

            # Assert
            assert cache.initialized is True
            instance.connect.assert_called_once()

    async def test_initialize_fails(self):
        """Test cache initialization failure."""
        # Setup
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.connected = False

            # Execute
            cache = DataCache(cache_ttl=60)
            await cache.initialize()

            # Assert
            assert cache.initialized is False
            instance.connect.assert_called_once()

    async def test_shutdown(self):
        """Test cache shutdown."""
        # Setup
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.close = AsyncMock()
            instance.connected = True

            # Execute
            cache = DataCache()
            await cache.initialize()
            await cache.shutdown()

            # Assert
            assert cache.initialized is False
            instance.close.assert_called_once()

    async def test_shutdown_when_not_initialized(self):
        """Test shutdown when cache is not initialized."""
        # Setup
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.close = AsyncMock()

            # Execute
            cache = DataCache()
            await cache.shutdown()

            # Assert
            instance.close.assert_not_called()

    async def test_get_user_data(self):
        """Test retrieving user data from cache."""
        # Setup
        test_data = {"id": "123", "name": "Test User"}
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.get = AsyncMock(return_value=test_data)
            instance.connected = True

            # Execute
            cache = DataCache()
            await cache.initialize()
            result = await cache.get_user_data("123")

            # Assert
            assert result == test_data
            instance.get.assert_called_once_with("user:123:data")

    async def test_get_user_data_not_initialized(self):
        """Test get user data when cache is not successfully initialized."""
        # Setup
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.connected = False

            # Execute
            cache = DataCache()
            result = await cache.get_user_data("123")  # Should try to initialize

            # Assert
            assert result is None
            instance.connect.assert_called_once()

    async def test_set_user_data(self):
        """Test setting user data in cache."""
        # Setup
        test_data = {"id": "123", "name": "Test User"}
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.set = AsyncMock(return_value=True)
            instance.connected = True

            # Execute
            cache = DataCache(cache_ttl=100)
            await cache.initialize()
            result = await cache.set_user_data("123", test_data)

            # Assert
            assert result is True
            instance.set.assert_called_once_with("user:123:data", test_data, 100)

    async def test_set_user_data_with_custom_ttl(self):
        """Test setting user data with custom TTL."""
        # Setup
        test_data = {"id": "123", "name": "Test User"}
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.set = AsyncMock(return_value=True)
            instance.connected = True

            # Execute
            cache = DataCache(cache_ttl=100)
            await cache.initialize()
            result = await cache.set_user_data("123", test_data, ttl=500)

            # Assert
            assert result is True
            instance.set.assert_called_once_with("user:123:data", test_data, 500)

    async def test_get_task_list(self):
        """Test retrieving task list from cache."""
        # Setup
        test_tasks = [{"id": 1, "title": "Task 1"}]
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.get = AsyncMock(return_value=test_tasks)
            instance.connected = True

            # Execute
            cache = DataCache()
            await cache.initialize()
            result = await cache.get_task_list("123", "default")

            # Assert
            assert result == test_tasks
            instance.get.assert_called_once_with("user:123:tasks:default")

    async def test_set_task_list(self):
        """Test setting task list in cache."""
        # Setup
        test_tasks = [{"id": 1, "title": "Task 1"}]
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.set = AsyncMock(return_value=True)
            instance.connected = True

            # Execute
            cache = DataCache(cache_ttl=60)
            await cache.initialize()
            result = await cache.set_task_list("123", "default", test_tasks)

            # Assert
            assert result is True
            instance.set.assert_called_once_with(
                "user:123:tasks:default", test_tasks, 60
            )

    async def test_invalidate_user_cache(self):
        """Test invalidating user cache."""
        # Setup
        with patch("core.data_cache.CacheManager") as mock_cache_manager_class:
            instance = mock_cache_manager_class.return_value
            instance.connect = AsyncMock()
            instance.delete = AsyncMock(return_value=True)
            instance.connected = True

            # Execute
            cache = DataCache()
            await cache.initialize()
            result = await cache.invalidate_user_cache("123")

            # Assert
            assert result is True
            instance.delete.assert_called_once_with("user:123:data")
