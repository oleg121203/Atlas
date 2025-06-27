import asyncio
import heapq
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    func: Callable = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    scheduled_time: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0


class TaskManager:
    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, Task] = {}
        self.task_queue = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.scheduled_tasks = []
        self.running = False

    async def add_task(self, task: Task) -> str:
        """Додає задачу до черги"""
        self.tasks[task.id] = task

        if task.scheduled_time is not None:
            heapq.heappush(self.scheduled_tasks, (task.scheduled_time, task.id))
        else:
            heapq.heappush(
                self.task_queue, (-task.priority.value, task.created_at, task.id)
            )

        return task.id

    async def start(self):
        """Start the task manager"""
        self.running = True
        asyncio.create_task(self._scheduler())
        asyncio.create_task(self._processor())

    async def stop(self):
        """Stop the task manager"""
        self.running = False
        for running_task in self.running_tasks.values():
            running_task.cancel()
        self.running_tasks.clear()

    async def _scheduler(self):
        """Process scheduled tasks"""
        while self.running:
            now = datetime.now()

            # Check if we have scheduled tasks ready to run
            while self.scheduled_tasks and self.scheduled_tasks[0][0] <= now:
                _, task_id = heapq.heappop(self.scheduled_tasks)
                if (
                    task_id in self.tasks
                    and self.tasks[task_id].status == TaskStatus.PENDING
                ):
                    heapq.heappush(
                        self.task_queue,
                        (
                            -self.tasks[task_id].priority.value,
                            self.tasks[task_id].created_at,
                            task_id,
                        ),
                    )

            await asyncio.sleep(0.1)  # Small sleep to prevent CPU hogging

    async def _processor(self):
        """Process pending tasks"""
        while self.running:
            # Check if we can start new tasks
            while (
                self.task_queue and len(self.running_tasks) < self.max_concurrent_tasks
            ):
                _, _, task_id = heapq.heappop(self.task_queue)
                if (
                    task_id in self.tasks
                    and self.tasks[task_id].status == TaskStatus.PENDING
                ):
                    self._start_task(self.tasks[task_id])

            await asyncio.sleep(0.1)  # Small sleep to prevent CPU hogging

    def _start_task(self, task: Task):
        """Start a task execution"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        async def _execute_task():
            try:
                if task.timeout:
                    result = await asyncio.wait_for(
                        self._run_task(task), timeout=task.timeout
                    )
                else:
                    result = await self._run_task(task)

                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
            except asyncio.TimeoutError:
                task.error = "Task timed out"
                await self._handle_task_failure(task)
            except Exception as e:
                task.error = str(e)
                await self._handle_task_failure(task)
            finally:
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]

        self.running_tasks[task.id] = asyncio.create_task(_execute_task())

    async def _run_task(self, task: Task):
        """Execute the task function"""
        if asyncio.iscoroutinefunction(task.func):
            return await task.func(*task.args, **task.kwargs)
        else:
            return task.func(*task.args, **task.kwargs)

    async def _handle_task_failure(self, task: Task):
        """Handle task failure and retry logic"""
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING

            # Schedule retry
            retry_time = datetime.now() + timedelta(seconds=task.retry_delay)
            task.scheduled_time = retry_time
            heapq.heappush(self.scheduled_tasks, (retry_time, task.id))
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task.status in [TaskStatus.PENDING, TaskStatus.RETRYING]:
            task.status = TaskStatus.CANCELLED
            return True
        elif task.status == TaskStatus.RUNNING and task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            task.status = TaskStatus.CANCELLED
            return True
        return False
