import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from ui.main_window import AtlasMainWindow
from utils.memory_management import MemoryManager


class MemoryManagementTest(unittest.TestCase):
    def setUp(self):
        # Ensure a QApplication instance exists for Qt operations
        if QCoreApplication.instance() is None:
            self.app = QApplication([])
        else:
            self.app = QCoreApplication.instance()
        # Mock dependencies
        self.mock_meta_agent = MagicMock()
        self.mock_meta_agent.agent_manager = MagicMock()

    @patch("utils.memory_management.psutil.Process")
    def test_memory_manager_initialization(self, mock_process):
        """Test initialization of MemoryManager with default settings."""
        # Mock memory info to return a specific value
        mock_mem_info = MagicMock()
        mock_mem_info.rss = 100 * 1024 * 1024  # 100MB
        mock_process.return_value.memory_info.return_value = mock_mem_info

        memory_manager = MemoryManager(cache_size_limit_mb=50, cache_ttl_minutes=10)
        self.assertEqual(
            memory_manager.cache_size_limit, 50 * 1024 * 1024
        )  # 50MB in bytes
        self.assertEqual(
            memory_manager.cache_ttl.total_seconds(), 600
        )  # 10 minutes in seconds
        self.assertEqual(
            memory_manager.get_memory_usage(), 100.0
        )  # Should return 100MB

    @patch("utils.memory_management.psutil.Process")
    def test_memory_usage_monitoring(self, mock_process):
        """Test memory usage monitoring functionality."""
        # Mock memory info to return increasing values
        mock_mem_info = MagicMock()
        mock_mem_info.rss = 200 * 1024 * 1024  # 200MB
        mock_process.return_value.memory_info.return_value = mock_mem_info

        memory_manager = MemoryManager()
        usage = memory_manager.get_memory_usage()
        self.assertEqual(usage, 200.0)  # Should return 200MB

        # Change the mock to simulate increased memory usage
        mock_mem_info.rss = 300 * 1024 * 1024  # 300MB
        usage = memory_manager.get_memory_usage()
        self.assertEqual(usage, 300.0)  # Should return 300MB

    def test_cache_management(self):
        """Test cache functionality with size limits and TTL."""
        memory_manager = MemoryManager(cache_size_limit_mb=1, cache_ttl_minutes=1)

        # Add items to cache
        result = memory_manager.add_to_cache("key1", "value1", size_estimate=100)
        self.assertTrue(result, "Item should be added to cache")
        self.assertEqual(
            memory_manager.get_from_cache("key1"),
            "value1",
            "Item should be retrievable from cache",
        )

        # Add another item
        result = memory_manager.add_to_cache("key2", "value2", size_estimate=100)
        self.assertTrue(result, "Second item should be added to cache")

        # Check cache size tracking (rough estimate, may not be exact due to sys.getsizeof)
        self.assertGreater(
            memory_manager.current_cache_size, 0, "Cache size should be greater than 0"
        )

    @patch("utils.memory_management.datetime")
    def test_cache_expiration(self, mock_datetime):
        """Test cache expiration based on TTL."""
        memory_manager = MemoryManager(cache_size_limit_mb=1, cache_ttl_minutes=1)

        # Mock datetime to simulate time passing
        start_time = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.now.return_value = start_time
        memory_manager.add_to_cache("key1", "value1", size_estimate=100)

        # Simulate time within TTL
        mock_datetime.now.return_value = start_time + timedelta(minutes=0.5)
        self.assertEqual(
            memory_manager.get_from_cache("key1"),
            "value1",
            "Item should still be in cache within TTL",
        )

        # Simulate time after TTL
        expired_time = start_time + timedelta(minutes=2)
        mock_datetime.now.return_value = expired_time
        self.assertIsNone(
            memory_manager.get_from_cache("key1"),
            "Item should be expired from cache after TTL",
        )

    @patch("ui_qt.main_window.QTimer")
    def test_memory_management_integration(self, mock_qtimer):
        """Test integration of MemoryManager with AtlasMainWindow."""
        # Mock QTimer to prevent actual timer execution during test
        mock_timer_instance = MagicMock()
        mock_qtimer.return_value = mock_timer_instance

        # Initialize main window
        main_window = AtlasMainWindow(meta_agent=self.mock_meta_agent)
        self.assertIsNotNone(
            main_window.memory_manager,
            "MemoryManager should be initialized in main window",
        )

        # Verify timer setup for memory management
        mock_timer_instance.timeout.connect.assert_called_once()
        mock_timer_instance.start.assert_called_once_with(300000)  # 5 minutes

        # Simulate memory management task with low memory usage
        with (
            patch.object(
                main_window.memory_manager, "get_memory_usage", return_value=200.0
            ),
            patch.object(
                main_window.memory_manager, "log_memory_stats"
            ) as mock_log_stats,
            patch.object(main_window.memory_manager, "perform_cleanup") as mock_cleanup,
        ):
            main_window._memory_management_task()
            mock_log_stats.assert_called_once()
            mock_cleanup.assert_not_called()

        # Simulate memory management task with high memory usage
        with (
            patch.object(
                main_window.memory_manager, "get_memory_usage", return_value=600.0
            ),
            patch.object(
                main_window.memory_manager, "log_memory_stats"
            ) as mock_log_stats,
            patch.object(main_window.memory_manager, "perform_cleanup") as mock_cleanup,
        ):
            main_window._memory_management_task()
            mock_log_stats.assert_called_once()
            mock_cleanup.assert_called_once()


if __name__ == "__main__":
    unittest.main()
