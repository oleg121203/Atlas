# __init__.py for ui/tasks directory

"""
This package contains UI components related to task management for the Atlas application.
"""

from .task_widget import TaskWidget
from .tasks_widget import TasksWidget

__all__ = ["TaskWidget", "TasksWidget"]
