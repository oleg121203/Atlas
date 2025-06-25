from typing import Dict, List, Optional

class MockTaskInstance:
    """Mock TaskInstance class for testing."""
    
    def __init__(self, id: str, name: str):
        """Initialize mock task instance."""
        self.id = id
        self.name = name
        self.status = "pending"
        
    def execute(self):
        """Mock execute method."""
        self.status = "completed"

class MockTaskManager:
    """Mock TaskManager class for testing."""
    
    def __init__(self, max_concurrent_tasks: int = 3, llm_manager: Optional['LLMManager'] = None):
        """Initialize mock task manager."""
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, MockTaskInstance] = {}
        self.running_tasks: Dict[str, MockTaskInstance] = {}
        self.completed_tasks: List[str] = []
        
    def create_task(self, task: Dict[str, str]):
        """Mock create_task method."""
        task_instance = MockTaskInstance(task['id'], task['name'])
        self.tasks[task['id']] = task_instance
        
    def execute_pending_tasks(self):
        """Mock execute_pending_tasks method."""
        pending_tasks = list(self.tasks.items())  # Create a copy to avoid dictionary size change
        for task_id, task in pending_tasks:
            if task.status == "pending":
                task.execute()
                self.running_tasks[task_id] = task
                self.completed_tasks.append(task_id)
                del self.tasks[task_id]

class MockAPIResourceManager:
    """Mock APIResourceManager class for testing."""
    
    def __init__(self):
        """Initialize mock API resource manager."""
        pass

class MockConfigManager:
    """Mock ConfigManager class for testing."""
    
    def __init__(self):
        """Initialize mock config manager."""
        pass
