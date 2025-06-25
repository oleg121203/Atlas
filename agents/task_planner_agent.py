# task_planner_agent.py

"""
Task Planner Agent module for Atlas.
This module implements the core functionality for autonomous task planning,
enabling the AI to independently plan, prioritize, and execute complex tasks
without direct user intervention.
"""

from typing import Dict, List, Any, Optional
import os
import json
from datetime import datetime, timedelta
import logging

from utils.logger import get_logger
from utils.memory_management import MemoryManager
from agents.self_learning_agent import SelfLearningAgent

logger = get_logger()

class TaskPlannerAgent:
    """A class to manage autonomous task planning for Atlas AI."""

    def __init__(self, memory_manager: MemoryManager, self_learning_agent: Optional[SelfLearningAgent] = None, plans_path: str = "plans"):
        """Initialize the TaskPlannerAgent with memory and learning dependencies.

        Args:
            memory_manager (MemoryManager): The memory manager instance for storing task history and context.
            self_learning_agent (SelfLearningAgent, optional): The self-learning agent for personalized planning. Defaults to None.
            plans_path (str): Path to store and load task plans.
        """
        self.memory_manager = memory_manager
        self.self_learning_agent = self_learning_agent
        self.plans_path = plans_path
        self.active_plans: Dict[str, Dict[str, Any]] = {}  # Dictionary to store active task plans by plan_id
        self.task_history: Dict[str, List[Dict[str, Any]]] = {}  # Historical task data by user_id
        if not os.path.exists(plans_path):
            os.makedirs(plans_path)
        self.load_plans()
        logger.info("TaskPlannerAgent initialized")

    def load_plans(self) -> None:
        """Load existing task plans from storage."""
        try:
            plans_file = os.path.join(self.plans_path, "active_plans.json")
            if os.path.exists(plans_file):
                with open(plans_file, 'r') as f:
                    self.active_plans = json.load(f)
                    logger.info(f"Loaded {len(self.active_plans)} active plans from storage")
            else:
                logger.debug("No existing plans file found, starting with empty plans")
        except Exception as e:
            logger.error(f"Failed to load plans: {e}")
            self.active_plans = {}

    def save_plans(self) -> None:
        """Save active task plans to storage."""
        try:
            plans_file = os.path.join(self.plans_path, "active_plans.json")
            with open(plans_file, 'w') as f:
                json.dump(self.active_plans, f, indent=2)
            logger.debug(f"Saved {len(self.active_plans)} active plans to storage")
        except Exception as e:
            logger.error(f"Failed to save plans: {e}")

    def create_task_plan(self, user_id: str, goal: str, context: Dict[str, Any] = None) -> str:
        """Create a new task plan based on a user goal and context.

        Args:
            user_id (str): Unique identifier for the user.
            goal (str): The user's goal or objective to achieve.
            context (Dict[str, Any], optional): Additional contextual information for planning. Defaults to None.

        Returns:
            str: The plan_id of the newly created plan.
        """
        if context is None:
            context = {}

        plan_id = f"plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        plan = {
            "plan_id": plan_id,
            "user_id": user_id,
            "goal": goal,
            "context": context,
            "tasks": self._break_down_goal(goal, context, user_id),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "progress": 0.0
        }

        self.active_plans[plan_id] = plan
        self.save_plans()
        logger.info(f"Created new task plan {plan_id} for user {user_id} with goal: {goal}")
        return plan_id

    def _break_down_goal(self, goal: str, context: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """Break down a goal into actionable sub-tasks.

        Args:
            goal (str): The user's goal to break down.
            context (Dict[str, Any]): Contextual information for planning.
            user_id (str): Unique identifier for the user.

        Returns:
            List[Dict[str, Any]]: List of sub-tasks with dependencies and priorities.
        """
        # For now, use a simple rule-based breakdown; later, integrate learning models
        tasks = []
        if "meeting" in goal.lower():
            tasks.append({
                "task_id": "task_1",
                "description": "Identify meeting participants",
                "priority": 1,
                "dependencies": [],
                "status": "pending",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "execution_method": "manual_user",
                "progress": 0.0
            })
            tasks.append({
                "task_id": "task_2",
                "description": "Schedule meeting time",
                "priority": 2,
                "dependencies": ["task_1"],
                "status": "pending",
                "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "execution_method": "plugin_calendar",
                "progress": 0.0
            })
            tasks.append({
                "task_id": "task_3",
                "description": "Send meeting invitations",
                "priority": 3,
                "dependencies": ["task_2"],
                "status": "pending",
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "execution_method": "plugin_email",
                "progress": 0.0
            })
        else:
            # Generic task breakdown as placeholder
            for i in range(1, 4):
                tasks.append({
                    "task_id": f"task_{i}",
                    "description": f"Step {i} towards {goal}",
                    "priority": i,
                    "dependencies": [f"task_{i-1}"] if i > 1 else [],
                    "status": "pending",
                    "due_date": (datetime.now() + timedelta(days=i)).isoformat(),
                    "execution_method": "manual_user",
                    "progress": 0.0
                })

        # Personalize task breakdown if self_learning_agent is available
        if self.self_learning_agent:
            user_profile = self.self_learning_agent.get_user_learning_profile(user_id)
            if user_profile.get("interaction_count", 0) > 5:
                avg_rating = user_profile.get("avg_rating", 3.0)
                if avg_rating > 4.0:
                    # If user rates highly, they might prefer fewer, broader tasks
                    tasks = self._consolidate_tasks(tasks)
                    logger.debug(f"Consolidated tasks for user {user_id} based on high satisfaction")

        return tasks

    def _consolidate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate a list of tasks into fewer, broader tasks.

        Args:
            tasks (List[Dict[str, Any]]): Original list of tasks.

        Returns:
            List[Dict[str, Any]]: Consolidated list of tasks.
        """
        if len(tasks) <= 1:
            return tasks

        consolidated = []
        main_task = tasks[0].copy()
        main_task["description"] = f"Complete main objective: {main_task['description']}"
        main_task["dependencies"] = []
        main_task["due_date"] = tasks[-1]["due_date"]
        consolidated.append(main_task)

        return consolidated

    def update_task_status(self, plan_id: str, task_id: str, status: str, progress: float = None) -> bool:
        """Update the status of a specific task within a plan.

        Args:
            plan_id (str): The ID of the plan containing the task.
            task_id (str): The ID of the task to update.
            status (str): The new status of the task (e.g., 'pending', 'in_progress', 'completed', 'failed').
            progress (float, optional): The progress percentage of the task (0.0 to 1.0). Defaults to None.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        if plan_id not in self.active_plans:
            logger.error(f"Plan {plan_id} not found for task status update")
            return False

        plan = self.active_plans[plan_id]
        task_found = False
        for task in plan["tasks"]:
            if task["task_id"] == task_id:
                task["status"] = status
                if progress is not None:
                    task["progress"] = progress
                elif status == "completed":
                    task["progress"] = 1.0
                elif status == "failed":
                    task["progress"] = 0.0
                task_found = True
                break

        if not task_found:
            logger.error(f"Task {task_id} not found in plan {plan_id}")
            return False

        # Update plan progress
        total_tasks = len(plan["tasks"])
        completed_tasks = sum(1 for t in plan["tasks"] if t["status"] == "completed")
        plan["progress"] = completed_tasks / total_tasks if total_tasks > 0 else 0.0
        plan["updated_at"] = datetime.now().isoformat()

        # Check if plan is complete
        if completed_tasks == total_tasks:
            plan["status"] = "completed"
            logger.info(f"Plan {plan_id} completed for user {plan['user_id']}")

        self.save_plans()
        logger.info(f"Updated task {task_id} in plan {plan_id} to status {status}")
        return True

    def execute_next_task(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Identify and execute the next feasible task in a plan.

        Args:
            plan_id (str): The ID of the plan to execute.

        Returns:
            Optional[Dict[str, Any]]: The task that was executed, or None if no task could be executed.
        """
        if plan_id not in self.active_plans:
            logger.error(f"Plan {plan_id} not found for task execution")
            return None

        plan = self.active_plans[plan_id]
        if plan["status"] != "active":
            logger.warning(f"Plan {plan_id} is not active, status: {plan['status']}")
            return None

        executable_task = None
        for task in plan["tasks"]:
            if task["status"] == "pending":
                # Check if all dependencies are completed
                dependencies_met = all(
                    any(t["task_id"] == dep and t["status"] == "completed" for t in plan["tasks"])
                    for dep in task["dependencies"]
                )
                if dependencies_met:
                    executable_task = task
                    break

        if executable_task:
            # Mark task as in progress
            self.update_task_status(plan_id, executable_task["task_id"], "in_progress")
            logger.info(f"Executing task {executable_task['task_id']} in plan {plan_id}")

            # Determine execution method and perform action
            execution_method = executable_task.get("execution_method", "manual_user")
            if execution_method == "manual_user":
                logger.debug(f"Task {executable_task['task_id']} requires user action: {executable_task['description']}")
                # Notify user through UI (to be implemented)
                return executable_task
            elif execution_method.startswith("plugin_"):
                plugin_name = execution_method.split("_", 1)[1]
                logger.debug(f"Task {executable_task['task_id']} to be executed via plugin: {plugin_name}")
                # Trigger plugin action (placeholder for actual plugin execution)
                try:
                    # Simulate plugin execution success for now
                    self.update_task_status(plan_id, executable_task["task_id"], "completed")
                except Exception as e:
                    logger.error(f"Plugin execution failed for task {executable_task['task_id']}: {e}")
                    self.update_task_status(plan_id, executable_task["task_id"], "failed")
                return executable_task
            else:
                logger.warning(f"Unknown execution method {execution_method} for task {executable_task['task_id']}")
                return executable_task
        else:
            logger.debug(f"No executable tasks found in plan {plan_id}")
            return None

    def get_active_plans(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all active plans for a specific user.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            List[Dict[str, Any]]: List of active plan dictionaries for the user.
        """
        user_plans = [plan for plan in self.active_plans.values() if plan["user_id"] == user_id and plan["status"] == "active"]
        logger.debug(f"Retrieved {len(user_plans)} active plans for user {user_id}")
        return user_plans

    def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve detailed information about a specific plan.

        Args:
            plan_id (str): The ID of the plan to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The plan dictionary if found, None otherwise.
        """
        if plan_id in self.active_plans:
            logger.debug(f"Retrieved details for plan {plan_id}")
            return self.active_plans[plan_id]
        logger.error(f"Plan {plan_id} not found")
        return None

    def cancel_plan(self, plan_id: str) -> bool:
        """Cancel a specific plan.

        Args:
            plan_id (str): The ID of the plan to cancel.

        Returns:
            bool: True if cancellation was successful, False otherwise.
        """
        if plan_id in self.active_plans:
            self.active_plans[plan_id]["status"] = "cancelled"
            self.active_plans[plan_id]["updated_at"] = datetime.now().isoformat()
            self.save_plans()
            logger.info(f"Cancelled plan {plan_id}")
            return True
        logger.error(f"Plan {plan_id} not found for cancellation")
        return False

    def adapt_plan(self, plan_id: str, new_context: Dict[str, Any]) -> bool:
        """Adapt an existing plan based on new context or user feedback.

        Args:
            plan_id (str): The ID of the plan to adapt.
            new_context (Dict[str, Any]): New contextual information for adaptation.

        Returns:
            bool: True if adaptation was successful, False otherwise.
        """
        if plan_id not in self.active_plans:
            logger.error(f"Plan {plan_id} not found for adaptation")
            return False

        plan = self.active_plans[plan_id]
        plan["context"].update(new_context)
        plan["updated_at"] = datetime.now().isoformat()

        # Re-evaluate tasks based on new context (placeholder for complex adaptation logic)
        for task in plan["tasks"]:
            if task["status"] == "pending":
                if "urgent" in new_context.get("priority", "").lower():
                    task["priority"] = max(task["priority"], 1)
                    task["due_date"] = (datetime.now() + timedelta(days=1)).isoformat()

        self.save_plans()
        logger.info(f"Adapted plan {plan_id} with new context")
        return True
