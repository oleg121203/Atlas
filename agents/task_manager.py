#!/usr/bin/env python3
"""
Task Manager for Atlas - Supports multiple concurrent goals with memory isolation

This module provides a task-based architecture that allows Atlas to run
multiple goals concurrently while maintaining complete memory isolation
between tasks.
"""

import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional

from agents.agent_manager import AgentManager
from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryType
from agents.master_agent import MasterAgent
from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager
from utils.logger import get_logger


class TaskStatus(Enum):
    """Status of a task execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for task execution."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskInstance:
    """Represents an isolated task instance with its own memory and context."""

    task_id: str
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    #Execution context
    execution_context: Dict[str, Any] = field(default_factory=dict)
    memory_scope: str = ""
    thread: Optional[threading.Thread] = None

    #Task configuration
    options: Dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    retry_count: int = 0

    #Results and errors
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0

    #Callbacks
    status_callback: Optional[Callable] = None
    progress_callback: Optional[Callable] = None

    def __post_init__(self):
        """Initialize memory scope if not provided."""
        if not self.memory_scope:
            self.memory_scope = f"task_{self.task_id}"


class APIResourceManager:
    """Manages API resources and rate limiting across multiple tasks."""

    def __init__(self, provider_limits: Dict[str, int] = None):
        """
        Initialize API resource manager.
        
        Args:
            provider_limits: Dict mapping provider names to requests per minute
        """
        self.provider_limits = provider_limits or {
            "openai": 60,    #requests per minute
            "ollama": 300,   #higher limit for local
            "anthropic": 50,
        }

        self.request_counters: Dict[str, List[float]] = {}
        self.request_locks: Dict[str, threading.Lock] = {}
        self.logger = get_logger()

        #Initialize locks for each provider
        for provider in self.provider_limits:
            self.request_locks[provider] = threading.Lock()

    def can_make_request(self, provider: str) -> bool:
        """Check if a request can be made to the provider."""
        if provider not in self.provider_limits:
            return True

        with self.request_locks[provider]:
            current_time = time.time()

            #Initialize counter if needed
            if provider not in self.request_counters:
                self.request_counters[provider] = []

            #Remove requests older than 1 minute
            self.request_counters[provider] = [
                req_time for req_time in self.request_counters[provider]
                if current_time - req_time < 60
            ]

            #Check if we can make another request
            return len(self.request_counters[provider]) < self.provider_limits[provider]

    def register_request(self, provider: str) -> bool:
        """Register a new API request."""
        if not self.can_make_request(provider):
            return False

        with self.request_locks[provider]:
            current_time = time.time()

            if provider not in self.request_counters:
                self.request_counters[provider] = []

            self.request_counters[provider].append(current_time)
            return True

    def wait_for_availability(self, provider: str, timeout: float = 60.0) -> bool:
        """Wait for API availability."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.can_make_request(provider):
                return True
            time.sleep(1)

        return False

    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all providers."""
        stats = {}
        current_time = time.time()

        for provider in self.provider_limits:
            with self.request_locks[provider]:
                if provider in self.request_counters:
                    #Count recent requests
                    recent_requests = [
                        req_time for req_time in self.request_counters[provider]
                        if current_time - req_time < 60
                    ]
                    requests_count = len(recent_requests)
                else:
                    requests_count = 0

                stats[provider] = {
                    "limit": self.provider_limits[provider],
                    "current_usage": requests_count,
                    "available": self.provider_limits[provider] - requests_count,
                    "utilization": (requests_count / self.provider_limits[provider]) * 100,
                }

        return stats


class TaskManager:
    """Manages multiple concurrent tasks with memory isolation."""

    def __init__(self,
                 max_concurrent_tasks: int = 3,
                 llm_manager: Optional[LLMManager] = None,
                 agent_manager: Optional[AgentManager] = None,
                 memory_db_path: Optional[str] = None):
        """
        Initialize the TaskManager.
        
        Args:
            max_concurrent_tasks: Maximum number of tasks to run concurrently
            llm_manager: LLM manager instance
            agent_manager: Agent manager instance
            memory_db_path: Path to ChromaDB database (not used, kept for compatibility)
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, TaskInstance] = {}
        self.task_queue = Queue()
        self.running_tasks: Dict[str, TaskInstance] = {}
        self.completed_tasks: List[str] = []

        #Managers
        if llm_manager is None:
            from agents.token_tracker import TokenTracker
            token_tracker = TokenTracker()
            self.llm_manager = LLMManager(token_tracker)
        else:
            self.llm_manager = llm_manager

        self.config_manager = ConfigManager()
        self.logger = get_logger()
        self.memory_manager = EnhancedMemoryManager(
            llm_manager=self.llm_manager,
            config_manager=self.config_manager,
            logger=self.logger,
        )

        self.agent_manager = agent_manager or AgentManager(
            llm_manager=self.llm_manager,
            memory_manager=self.memory_manager,
        )
        self.api_resource_manager = APIResourceManager()

        #Synchronization
        self.tasks_lock = threading.Lock()
        self.shutdown_event = threading.Event()

        #Task scheduler thread
        self.scheduler_thread = threading.Thread(target=self._task_scheduler, daemon=True)
        self.scheduler_running = True

        # Initialize required collections in memory manager
        self._initialize_collections()

        self.logger.info(f"TaskManager initialized with max {max_concurrent_tasks} concurrent tasks")

    def start(self):
        """Start the task manager."""
        if not self.scheduler_thread.is_alive():
            self.scheduler_thread.start()
            self.logger.info("TaskManager started")

    def stop(self):
        """Stop the task manager and all running tasks."""
        self.scheduler_running = False
        self.shutdown_event.set()

        #Stop all running tasks
        with self.tasks_lock:
            for task_id, task in list(self.running_tasks.items()):
                self.cancel_task(task_id)

        #Wait for scheduler to finish
        if self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=10)

        self.logger.info("TaskManager stopped")

    def create_task(self,
                   goal: str,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   options: Dict[str, Any] = None,
                   status_callback: Callable = None,
                   progress_callback: Callable = None) -> str:
        """
        Create a new task.
        
        Args:
            goal: The goal to accomplish
            priority: Task priority
            options: Additional task options
            status_callback: Callback for status updates
            progress_callback: Callback for progress updates
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())[:8]

        task = TaskInstance(
            task_id=task_id,
            goal=goal,
            priority=priority,
            options=options or {},
            status_callback=status_callback,
            progress_callback=progress_callback,
        )

        with self.tasks_lock:
            self.tasks[task_id] = task
            self.task_queue.put(task_id)

        #Store task creation in memory
        self._store_task_event(task_id, "created", {"goal": goal, "priority": priority.value})

        self.logger.info(f"Created task {task_id}: {goal[:50]}...")
        return task_id

    def get_task(self, task_id: str) -> Optional[TaskInstance]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get task status."""
        task = self.get_task(task_id)
        return task.status if task else None

    def pause_task(self, task_id: str) -> bool:
        """Pause a running task."""
        with self.tasks_lock:
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.PAUSED
                self._store_task_event(task_id, "paused")
                self.logger.info(f"Paused task {task_id}")
                return True
        return False

    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task."""
        with self.tasks_lock:
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.PAUSED:
                task.status = TaskStatus.PENDING
                self.task_queue.put(task_id)  #Re-queue the task
                self._store_task_event(task_id, "resumed")
                self.logger.info(f"Resumed task {task_id}")
                return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        with self.tasks_lock:
            task = self.tasks.get(task_id)
            if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.PAUSED]:
                task.status = TaskStatus.CANCELLED

                #Stop the thread if running
                if task.thread and task.thread.is_alive():
                    #Note: Python doesn't support forceful thread termination
                    #The task should check for cancellation status periodically
                    pass

                #Remove from running tasks
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]

                self._store_task_event(task_id, "cancelled")
                self.logger.info(f"Cancelled task {task_id}")
                return True
        return False

    def get_all_tasks(self) -> Dict[str, TaskInstance]:
        """Get all tasks."""
        return self.tasks.copy()

    def get_running_tasks(self) -> Dict[str, TaskInstance]:
        """Get currently running tasks."""
        return self.running_tasks.copy()

    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task execution statistics."""
        with self.tasks_lock:
            stats = {
                "total_tasks": len(self.tasks),
                "running": len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
                "pending": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
                "completed": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
                "failed": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
                "cancelled": len([t for t in self.tasks.values() if t.status == TaskStatus.CANCELLED]),
                "paused": len([t for t in self.tasks.values() if t.status == TaskStatus.PAUSED]),
                "max_concurrent": self.max_concurrent_tasks,
                "api_stats": self.api_resource_manager.get_provider_stats(),
            }
        return stats

    def _task_scheduler(self):
        """Main task scheduling loop."""
        self.logger.info("Task scheduler started")

        while self.scheduler_running and not self.shutdown_event.is_set():
            try:
                #Check if we can start more tasks
                if len(self.running_tasks) < self.max_concurrent_tasks:
                    try:
                        #Get next task from queue (with timeout)
                        task_id = self.task_queue.get(timeout=1.0)

                        with self.tasks_lock:
                            task = self.tasks.get(task_id)

                            if task and task.status == TaskStatus.PENDING:
                                #Check API availability
                                provider = self._get_task_provider(task)
                                if self.api_resource_manager.can_make_request(provider):
                                    self._start_task(task)
                                else:
                                    #Re-queue if API not available
                                    self.task_queue.put(task_id)
                                    self.logger.debug(f"Re-queued task {task_id} - API not available")

                    except Empty:
                        #No tasks in queue, continue
                        pass

                #Clean up completed tasks from running_tasks
                completed_task_ids = []
                with self.tasks_lock:
                    for task_id, task in list(self.running_tasks.items()):
                        if task.status not in [TaskStatus.RUNNING, TaskStatus.PAUSED]:
                            completed_task_ids.append(task_id)

                for task_id in completed_task_ids:
                    if task_id in self.running_tasks:
                        del self.running_tasks[task_id]

                time.sleep(0.5)  #Small delay to prevent busy waiting

            except Exception as e:
                self.logger.error(f"Error in task scheduler: {e}", exc_info=True)
                time.sleep(1)

        self.logger.info("Task scheduler stopped")

    def _start_task(self, task: TaskInstance):
        """Start executing a task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        #Create isolated agent instances for this task
        isolated_agents = self._create_isolated_agents(task.memory_scope)

        #Create and start task thread
        task.thread = threading.Thread(
            target=self._execute_task,
            args=(task, isolated_agents),
            daemon=True,
        )

        self.running_tasks[task.task_id] = task
        task.thread.start()

        self._store_task_event(task.task_id, "started")
        self.logger.info(f"Started task {task.task_id}")

    def _execute_task(self, task: TaskInstance, isolated_agents: Dict[str, Any]):
        """Execute a task in isolation."""
        try:
            self.logger.info(f"Executing task {task.task_id}: {task.goal}")

            #Get the isolated master agent
            master_agent = isolated_agents["master_agent"]

            #Set up status callback that updates task progress and push through to UI
            def task_status_callback(status_info: Dict[str, Any]):
                # Forward to any external consumer (e.g. UI)
                if task.status_callback:
                    try:
                        task.status_callback(status_info)
                    except Exception:
                        self.logger.exception("Task status_callback raised")

                # Update internal TaskInstance progress if provided in payload
                if isinstance(status_info, dict) and "progress" in status_info:
                    task.progress = float(status_info["progress"])
                    if task.progress_callback:
                        try:
                            task.progress_callback(task.task_id, task.progress, status_info.get("message", ""))
                        except Exception:
                            self.logger.exception("Task progress_callback raised")

            # Inject callback into master agent before execution
            master_agent.status_callback = task_status_callback

            #Execute the goal using isolated master agent
            master_agent.run(
                goal=task.goal,
                master_prompt=task.options.get("prompt", "Complete the given goal efficiently."),
                options=task.options,
            )

            #Wait for completion or check for cancellation
            while master_agent.is_running and task.status == TaskStatus.RUNNING:
                time.sleep(0.5)

                #Check if task was cancelled
                if task.status == TaskStatus.CANCELLED:
                    master_agent.stop()
                    break

            #Determine final status
            if task.status == TaskStatus.CANCELLED:
                task.result = "Task was cancelled"
            elif master_agent.is_running:
                #Something went wrong
                task.status = TaskStatus.FAILED
                task.error = "Task execution incomplete"
            else:
                #Task completed successfully
                task.status = TaskStatus.COMPLETED
                task.result = "Task completed successfully"
                task.progress = 100.0

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.logger.error(f"Task {task.task_id} failed: {e}", exc_info=True)

        finally:
            task.completed_at = datetime.now()
            self._store_task_event(
                task.task_id,
                "completed",
                {
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error,
                    "duration": (task.completed_at - task.started_at).total_seconds() if task.started_at else None,
                },
            )

            self.logger.info(f"Task {task.task_id} finished with status: {task.status.value}")

    def _create_isolated_agents(self, memory_scope: str) -> Dict[str, Any]:
        """Create isolated agent instances for a task."""
        #Create a new master agent with isolated memory
        master_agent = MasterAgent(
            llm_manager=self.llm_manager,
            agent_manager=self.agent_manager,
            memory_manager=self.memory_manager,  #Will use task-specific scope
        )

        #Set the memory scope for isolation
        master_agent.memory_scope = memory_scope

        return {
            "master_agent": master_agent,
        }

    def _get_task_provider(self, task: TaskInstance) -> str:
        """Get the LLM provider for a task."""
        #This could be configurable per task
        return task.options.get("provider", "openai")

    def _store_task_event(self, task_id: str, event_type: str, metadata: Dict[str, Any] = None):
        """Store task events in memory."""
        try:
            content = {
                "task_id": task_id,
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
            }

            if metadata:
                content.update(metadata)

            self.memory_manager.store_memory(
                agent_name=f"task_{task_id}",
                memory_type=MemoryType.SYSTEM_STATUS,
                content=content,
                metadata={"event_type": event_type, "task_id": task_id},
            )
        except Exception as e:
            self.logger.warning(f"Failed to store task event: {e}")

    def _initialize_collections(self):
        """Initialize required database collections."""
        required_collections = [
            "global_success",      # For task success tracking
            "global_interaction",  # For task interactions
            "global_memory",      # For shared memory
            "task_registry",      # For task metadata
        ]
        
        if self.memory_manager:
            for collection in required_collections:
                try:
                    if not self.memory_manager.collection_exists(collection):
                        self.memory_manager.create_collection(collection)
                        self.logger.info(f"Created collection: {collection}")
                except Exception as e:
                    self.logger.error(f"Failed to create collection {collection}: {str(e)}")
                    
    def _ensure_task_collections(self, task_id: str):
        """Ensure task-specific collections exist."""
        task_collections = [
            f"task_{task_id}_success",
            f"task_{task_id}_interaction",
            f"task_{task_id}_memory"
        ]
        
        if self.memory_manager:
            for collection in task_collections:
                try:
                    if not self.memory_manager.collection_exists(collection):
                        self.memory_manager.create_collection(collection)
                except Exception as e:
                    self.logger.error(f"Failed to create task collection {collection}: {str(e)}")

    def handle_browser_goal(self, task: TaskInstance) -> bool:
        """
        Handle browser-related goals.
        
        Args:
            task: The task instance to handle
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Extract browser name and URL from goal
            import re
            goal_lower = task.goal.lower()
            
            # Check if this is a browser task
            browser_keywords = ["browser", "браузер", "safari", "chrome", "firefox", "edge"]
            if not any(keyword in goal_lower for keyword in browser_keywords):
                return False
                
            # Get browser agent
            browser_agent = self.agent_manager.get_agent("browser")
            if not browser_agent:
                self.logger.error("Browser agent not available")
                return False
                
            # Execute the browser task
            result = browser_agent.execute_task(task.goal, task.execution_context)
            
            # Store the result
            self._store_task_result(task.task_id, result)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Browser task execution failed: {str(e)}")
            self._store_task_error(task.task_id, str(e))
            return False
            
    def _store_task_result(self, task_id: str, result: Any):
        """Store task execution result."""
        try:
            if self.memory_manager:
                # Store in global collection
                success1 = self.memory_manager.store_memory_safe(
                    "global_success",
                    MemoryType.SUCCESS,
                    {
                        "task_id": task_id,
                        "result": str(result),
                        "timestamp": time.time()
                    }
                )
                
                # Also store in task-specific collection
                success2 = self.memory_manager.store_memory_safe(
                    f"task_{task_id}_success",
                    MemoryType.SUCCESS,
                    {
                        "result": str(result),
                        "timestamp": time.time()
                    }
                )
                
                if not (success1 and success2):
                    self.logger.warning(f"Partial failure storing task result for {task_id}")
        except Exception as e:
            self.logger.error(f"Failed to store task result: {str(e)}")
            
    def _store_task_error(self, task_id: str, error: str):
        """Store task execution error."""
        try:
            if self.memory_manager:
                # Store in global collection
                success1 = self.memory_manager.store_memory_safe(
                    "global_success",
                    MemoryType.ERROR,
                    {
                        "task_id": task_id,
                        "error": error,
                        "timestamp": time.time()
                    }
                )
                
                # Also store in task-specific collection
                success2 = self.memory_manager.store_memory_safe(
                    f"task_{task_id}_success",
                    MemoryType.ERROR,
                    {
                        "error": error,
                        "timestamp": time.time()
                    }
                )
                
                if not (success1 and success2):
                    self.logger.warning(f"Partial failure storing task error for {task_id}")
        except Exception as e:
            self.logger.error(f"Failed to store task error: {str(e)}")


#Example usage and demo
def demo_task_manager():
    """Demonstrate the TaskManager functionality."""
    print("🚀 TaskManager Demo - Multiple Concurrent Goals")
    print("=" * 60)

    #Initialize task manager
    task_manager = TaskManager(max_concurrent_tasks=3)
    task_manager.start()

    try:
        #Create multiple tasks
        tasks = []

        task1_id = task_manager.create_task(
            "Take a screenshot of the desktop",
            priority=TaskPriority.HIGH,
        )
        tasks.append(task1_id)
        print(f"✅ Created Task 1: {task1_id}")

        task2_id = task_manager.create_task(
            "Check the current weather in Kyiv",
            priority=TaskPriority.NORMAL,
        )
        tasks.append(task2_id)
        print(f"✅ Created Task 2: {task2_id}")

        task3_id = task_manager.create_task(
            "Count the number of running processes",
            priority=TaskPriority.LOW,
        )
        tasks.append(task3_id)
        print(f"✅ Created Task 3: {task3_id}")

        #Monitor task execution
        print("\n📊 Monitoring task execution...")

        for i in range(20):  #Monitor for 20 seconds
            stats = task_manager.get_task_statistics()
            running_tasks = task_manager.get_running_tasks()

            print(f"\n🕐 Time: {i+1}s")
            print(f"   Running: {stats['running']} | Pending: {stats['pending']} | Completed: {stats['completed']}")

            if running_tasks:
                for task_id, task in running_tasks.items():
                    print(f"   🏃 {task_id}: {task.goal[:40]}... ({task.status.value})")

            #Check if all tasks are done
            if stats["running"] == 0 and stats["pending"] == 0:
                break

            time.sleep(1)

        #Final statistics
        print("\n📈 Final Statistics:")
        final_stats = task_manager.get_task_statistics()
        for key, value in final_stats.items():
            if key != "api_stats":
                print(f"   {key}: {value}")

        print("\n🔍 Task Details:")
        for task_id in tasks:
            task = task_manager.get_task(task_id)
            if task:
                duration = "N/A"
                if task.started_at and task.completed_at:
                    duration = f"{(task.completed_at - task.started_at).total_seconds():.1f}s"

                print(f"   📋 {task_id}:")
                print(f"      Goal: {task.goal}")
                print(f"      Status: {task.status.value}")
                print(f"      Duration: {duration}")
                if task.error:
                    print(f"      Error: {task.error}")

        #API Usage Statistics
        print("\n🌐 API Usage Statistics:")
        api_stats = final_stats["api_stats"]
        for provider, stats in api_stats.items():
            print(f"   {provider}: {stats['current_usage']}/{stats['limit']} ({stats['utilization']:.1f}%)")

    finally:
        task_manager.stop()
        print("\n🎉 TaskManager demo completed!")


if __name__ == "__main__":
    demo_task_manager()
