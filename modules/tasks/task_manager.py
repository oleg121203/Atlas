from typing import Dict, List, Any

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, List[Dict[str, Any]]] = {}

    def add_task(self, user_id: str, task_description: str) -> str:
        """Add a task for a user and return the task ID."""
        if user_id not in self.tasks:
            self.tasks[user_id] = []
        
        task_id = f"task_{len(self.tasks[user_id]) + 1}"
        task = {
            'task_id': task_id,
            'description': task_description,
            'status': 'pending',
            'progress': 0.0
        }
        self.tasks[user_id].append(task)
        return task_id

    def get_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a user."""
        return self.tasks.get(user_id, [])

    def update_task_status(self, user_id: str, task_id: str, status: str) -> bool:
        """Update the status of a specific task."""
        if user_id in self.tasks:
            for task in self.tasks[user_id]:
                if task['task_id'] == task_id:
                    task['status'] = status
                    if status == 'completed':
                        task['progress'] = 1.0
                    elif status == 'in_progress':
                        task['progress'] = 0.5
                    return True
        return False
