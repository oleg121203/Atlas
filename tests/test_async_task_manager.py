# tests/test_async_task_manager.py

import unittest
import time
import logging
from core.async_task_manager import AsyncTaskManager

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAsyncTaskManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.task_manager = AsyncTaskManager()
        self.task_manager.start()
        self.result = None

    def tearDown(self):
        """Clean up after tests."""
        self.task_manager.stop()

    def test_task_execution(self):
        """Test basic task execution."""
        def simple_task():
            time.sleep(0.1)
            return "Task completed"

        def callback(result):
            self.result = result

        self.task_manager.submit_task(simple_task, callback)
        time.sleep(0.2)  # Wait for task to complete
        self.assertEqual(self.result, "Task completed")

    def test_multiple_tasks(self):
        """Test execution of multiple tasks."""
        results = []

        def task1():
            time.sleep(0.1)
            return "Result 1"

        def task2():
            time.sleep(0.1)
            return "Result 2"

        def callback(result):
            results.append(result)

        self.task_manager.submit_task(task1, callback)
        self.task_manager.submit_task(task2, callback)
        time.sleep(0.3)  # Wait for tasks to complete
        self.assertEqual(len(results), 2)
        self.assertTrue("Result 1" in results)
        self.assertTrue("Result 2" in results)

    def test_task_with_error(self):
        """Test handling of task that raises an error."""
        def error_task():
            raise ValueError("Test error")

        def callback(result):
            self.result = result

        self.task_manager.submit_task(error_task, callback)
        time.sleep(0.2)  # Wait for task to complete
        self.assertIsNone(self.result)  # Callback should not be called on error

    def test_queue_size(self):
        """Test queue size reporting."""
        def slow_task():
            time.sleep(0.5)
            return "Slow task"

        self.task_manager.submit_task(slow_task)
        self.task_manager.submit_task(slow_task)
        time.sleep(0.1)  # Allow tasks to be queued but not completed
        self.assertGreaterEqual(self.task_manager.get_queue_size(), 1)

if __name__ == '__main__':
    unittest.main()
