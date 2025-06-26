# core/async_task_manager.py

import threading
import queue
import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger("AsyncTaskManager")

class AsyncTaskManager:
    """Manages asynchronous execution of tasks to prevent UI blocking."""

    def __init__(self):
        self.task_queue = queue.Queue()
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        logger.info("AsyncTaskManager initialized")

    def start(self):
        """Start the worker thread to process tasks asynchronously."""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
            self.worker_thread.start()
            logger.info("AsyncTaskManager started")

    def stop(self):
        """Stop the worker thread and wait for it to finish."""
        if self.is_running:
            self.is_running = False
            if self.worker_thread:
                self.worker_thread.join()
                self.worker_thread = None
            logger.info("AsyncTaskManager stopped")

    def submit_task(self, task: Callable[[], Any], callback: Optional[Callable[[Any], None]] = None):
        """Submit a task to be executed asynchronously.

        Args:
            task: The task function to execute.
            callback: Optional callback function to call with the result after task completion.
        """
        self.task_queue.put((task, callback))
        logger.debug(f"Task submitted to queue, current queue size: {self.task_queue.qsize()}")

    def _process_tasks(self):
        """Process tasks from the queue in a separate thread."""
        while self.is_running:
            try:
                # Get a task from the queue with a timeout to check if still running
                task, callback = self.task_queue.get(timeout=1.0)
                logger.debug("Processing task from queue")
                try:
                    result = task()
                    if callback:
                        callback(result)
                    logger.debug("Task completed successfully")
                except Exception as e:
                    logger.error(f"Error executing task: {str(e)}", exc_info=True)
                finally:
                    self.task_queue.task_done()
            except queue.Empty:
                continue  # Queue is empty, check if still running
            except Exception as e:
                logger.error(f"Unexpected error in task processing: {str(e)}", exc_info=True)
                time.sleep(1)  # Prevent tight CPU loop in case of repeated errors

    def get_queue_size(self) -> int:
        """Get the current number of tasks in the queue.

        Returns:
            int: Number of tasks waiting to be processed.
        """
        return self.task_queue.qsize()
