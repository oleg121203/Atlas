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
import uuid
import time

from core.ethics.ethical_guidelines import EthicalGuidelines, EthicalPrinciple
from utils.logger import get_logger
from utils.memory_management import MemoryManager
from modules.agents.self_learning_agent import SelfLearningAgent

logger = get_logger()

# Cache for storing frequently used results
class SimpleCache:
    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Tuple[any, float]] = {}
        self.ttl = ttl  # Time to live in seconds

    def get(self, key: str) -> Optional[any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: any) -> None:
        self.cache[key] = (value, time.time())

    def clear(self) -> None:
        self.cache.clear()

# Initialize cache for task planner
_plan_cache = SimpleCache(ttl=1800)  # Cache for 30 minutes

class TaskPlannerAgent:
    """An agent responsible for creating, updating, and managing tasks and plans with ethical considerations."""

    def __init__(self, memory_manager: MemoryManager, self_learning_agent: Optional[SelfLearningAgent] = None, plans_path: str = "plans", user_id: str = "default_user"):
        """Initialize the TaskPlannerAgent with memory management and ethical guidelines.

        Args:
            memory_manager (MemoryManager): The memory manager instance for storing task history and context.
            self_learning_agent (SelfLearningAgent, optional): The self-learning agent for personalized planning. Defaults to None.
            plans_path (str): Path to store and load task plans.
            user_id (str): Unique identifier for the user.
        """
        self.memory_manager = memory_manager
        self.self_learning_agent = self_learning_agent
        self.plans_path = plans_path
        self.user_id = user_id
        self.active_plans: Dict[str, Dict[str, Any]] = {}  # Dictionary to store active task plans by plan_id
        self.task_history: Dict[str, List[Dict[str, Any]]] = {}  # Historical task data by user_id
        self.ethics = EthicalGuidelines()
        self.performance_metrics = []
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
        start_time = time.time()
        if context is None:
            context = {}

        plan_id = f"plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        plan = {
            "plan_id": plan_id,
            "user_id": user_id,
            "goal": goal,
            "context": context,
            "tasks": self._break_down_goal(goal, context, user_id),
            "status": "pending_user_consent",  # Ethical AI: Require user consent before proceeding
            "ethical_flags": {
                "user_consent_required": True,
                "consent_status": "pending",
                "notification_sent": False
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "progress": 0.0
        }

        self.active_plans[plan_id] = plan
        self.save_plans()
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("create_task_plan", latency)
        logger.info(f"Created new task plan {plan_id} for user {user_id} with goal: {goal}, Latency: {latency:.2f}ms")
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
        """Update the status of a specific task within a plan, ensuring ethical compliance.

        Args:
            plan_id (str): The ID of the plan containing the task.
            task_id (str): The ID of the task to update.
            status (str): The new status of the task (e.g., 'pending', 'in_progress', 'completed', 'failed').
            progress (float, optional): The progress percentage of the task (0.0 to 1.0). Defaults to None.

        Returns:
            bool: True if update was successful and ethical, False otherwise.
        """
        start_time = time.time()
        if plan_id not in self.active_plans:
            logger.error(f"Plan {plan_id} not found for task status update")
            return False

        plan = self.active_plans[plan_id]
        # Ethical AI: Check for user consent before updating task status
        if plan.get("ethical_flags", {}).get("consent_status", "pending") != "granted":
            logger.warning(f"Cannot update task {task_id} in plan {plan_id}: User consent not granted")
            return False

        # Prepare context for ethical evaluation
        context = {
            "explanation": f"Updating task {task_id} to status {status} in plan {plan_id}",
            "audit_log": True,
            "bias_check": True,
            "data_protection": "user_data" not in plan or plan.get("anonymized", False),
            "user_benefit": status == "completed" or status == "in_progress"
        }
        is_ethical, scores, explanation = self.ethics.is_action_ethical(
            f"Update task {task_id} status to {status}", context
        )
        
        if not is_ethical:
            logger.warning(f"Ethical violation in task update: {explanation}")
            return False
        
        # Check user consent for task updates involving personal data
        if "user_data" in plan and not self.ethics.check_consent(plan["user_id"], "task_update"):
            logger.warning(f"User {plan['user_id']} has not consented to task updates with personal data")
            return False
        
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
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("update_task_status", latency)
        logger.info(f"Updated task {task_id} in plan {plan_id} to status {status}, Latency: {latency:.2f}ms")
        return True

    def execute_next_task(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Identify and execute the next feasible task in a plan.

        Args:
            plan_id (str): The ID of the plan to execute.

        Returns:
            Optional[Dict[str, Any]]: The task that was executed, or None if no task could be executed.
        """
        start_time = time.time()
        if plan_id not in self.active_plans:
            logger.error(f"Plan {plan_id} not found for task execution")
            return None

        plan = self.active_plans[plan_id]
        if plan["status"] != "active":
            logger.warning(f"Plan {plan_id} is not active, status: {plan['status']}")
            return None

        # Ethical AI: Check for user consent before executing tasks
        if plan.get("ethical_flags", {}).get("consent_status", "pending") != "granted":
            logger.warning(f"Cannot execute tasks in plan {plan_id}: User consent not granted")
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
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("execute_next_task", latency)

    def get_active_plans(self, user_id: str = None):
        """Retrieve all active plans, optionally filtered by user ID.

        Args:
            user_id: Optional user ID to filter plans. If None, returns all plans.

        Returns:
            Dictionary of active plans, filtered by user ID if provided.
        """
        start_time = time.time()
        if user_id is None:
            result = self.active_plans
        else:
            result = {plan_id: plan for plan_id, plan in self.active_plans.items() if plan.get("user_id") == user_id}
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("get_active_plans", latency)
        return result

    def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve detailed information about a specific plan.

        Args:
            plan_id (str): The ID of the plan to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The plan dictionary if found, None otherwise.
        """
        start_time = time.time()
        if plan_id in self.active_plans:
            logger.debug(f"Retrieved details for plan {plan_id}")
            result = self.active_plans[plan_id]
        else:
            logger.error(f"Plan {plan_id} not found")
            result = None
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("get_plan_details", latency)
        return result

    def cancel_plan(self, plan_id: str) -> bool:
        """Cancel a specific plan.

        Args:
            plan_id (str): The ID of the plan to cancel.

        Returns:
            bool: True if cancellation was successful, False otherwise.
        """
        start_time = time.time()
        if plan_id in self.active_plans:
            self.active_plans[plan_id]["status"] = "cancelled"
            self.active_plans[plan_id]["updated_at"] = datetime.now().isoformat()
            self.save_plans()
            logger.info(f"Cancelled plan {plan_id}")
            result = True
        else:
            logger.error(f"Plan {plan_id} not found for cancellation")
            result = False
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("cancel_plan", latency)
        return result

    def adapt_plan(self, plan_id: str, new_context: Dict[str, Any]) -> bool:
        """Adapt an existing plan based on new context or user feedback.

        Args:
            plan_id (str): The ID of the plan to adapt.
            new_context (Dict[str, Any]): New contextual information for adaptation.

        Returns:
            bool: True if adaptation was successful, False otherwise.
        """
        start_time = time.time()
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
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("adapt_plan", latency)
        return True

    def confirm_user_consent(self, plan_id: str, consent_granted: bool) -> bool:
        """Record user consent for a plan's execution.

        Args:
            plan_id (str): The ID of the plan requiring consent.
            consent_granted (bool): Whether the user grants consent for the plan.

        Returns:
            bool: True if consent status was updated, False otherwise.
        """
        start_time = time.time()
        if plan_id not in self.active_plans:
            logger.error(f"Plan {plan_id} not found for consent confirmation")
            return False

        plan = self.active_plans[plan_id]
        ethical_flags = plan.get("ethical_flags", {})
        if ethical_flags.get("user_consent_required", False):
            ethical_flags["consent_status"] = "granted" if consent_granted else "denied"
            plan["status"] = "active" if consent_granted else "rejected_by_user"
            plan["updated_at"] = datetime.now().isoformat()
            self.save_plans()
            logger.info(f"User consent for plan {plan_id} updated to: {'granted' if consent_granted else 'denied'}")
            result = True
        else:
            logger.warning(f"Plan {plan_id} does not require user consent")
            result = False
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("confirm_user_consent", latency)
        return result

    def get_tasks(self):
        """Retrieve all tasks from active plans.

        Returns:
            List of tasks across all active plans.
        """
        start_time = time.time()
        tasks = []
        for plan_id, plan in self.active_plans.items():
            tasks.extend(plan.get("tasks", []))
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("get_tasks", latency)
        return tasks

    def create_task(self, plan_id: str, task_description: str, priority: int = 3) -> bool:
        """Create a new task within a specified plan, with safety checks to prevent harmful actions.

        Args:
            plan_id: Unique identifier for the plan.
            task_description: Description of the task.
            priority: Priority level for the task (1-5).

        Returns:
            Boolean indicating if the task was created successfully and is safe.
        """
        start_time = time.time()
        active_plans = self.get_active_plans()
        for plan in active_plans.values():
            if plan["plan_id"] == plan_id:
                # Safety check for potentially harmful actions
                context = {
                    "explanation": f"Creating task: {task_description} in plan {plan_id}",
                    "audit_log": True,
                    "bias_check": True,
                    "data_protection": True,
                    "user_benefit": True
                }
                is_ethical, scores, explanation = self.ethics.is_action_ethical(
                    f"Create task: {task_description}", context
                )
                
                if not is_ethical:
                    logger.warning(f"Ethical violation in task creation: {explanation}")
                    return False
                
                # Additional safety check for harmful keywords or actions
                harmful_keywords = ["delete", "destroy", "harm", "attack", "disable", "shutdown"]
                if any(keyword in task_description.lower() for keyword in harmful_keywords):
                    logger.warning(f"Potential harmful task detected: {task_description}")
                    return False
                
                new_task = {
                    "task_id": str(uuid.uuid4()),
                    "description": task_description,
                    "status": "pending",
                    "priority": max(1, min(5, priority)),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                plan.setdefault("tasks", []).append(new_task)
                if self.memory_manager:
                    self.memory_manager.store("plans", active_plans)
                logger.info(f"Created task in plan {plan_id}: {task_description}")
                result = True
                break
        else:
            result = False
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("create_task", latency)
        return result

    def update_task_status(self, plan_id: str, task_id: str, new_status: str) -> bool:
        """Update the status of a task within a plan, ensuring ethical compliance.

        Args:
            plan_id: Unique identifier for the plan.
            task_id: Unique identifier for the task.
            new_status: New status for the task.

        Returns:
            Boolean indicating if the update was successful and ethical.
        """
        start_time = time.time()
        active_plans = self.get_active_plans()
        for plan in active_plans.values():
            if plan["plan_id"] == plan_id:
                for task in plan.get("tasks", []):
                    if task["task_id"] == task_id:
                        # Prepare context for ethical evaluation
                        context = {
                            "explanation": f"Updating task {task_id} to status {new_status} in plan {plan_id}",
                            "audit_log": True,
                            "bias_check": True,
                            "data_protection": "user_data" not in task or task.get("anonymized", False),
                            "user_benefit": new_status == "completed" or new_status == "in_progress"
                        }
                        is_ethical, scores, explanation = self.ethics.is_action_ethical(
                            f"Update task {task_id} status to {new_status}", context
                        )
                        
                        if not is_ethical:
                            logger.warning(f"Ethical violation in task update: {explanation}")
                            return False
                        
                        # Check user consent for task updates involving personal data
                        if "user_data" in task and not self.ethics.check_consent(self.user_id, "task_update"):
                            logger.warning(f"User {self.user_id} has not consented to task updates with personal data")
                            return False
                        
                        task["status"] = new_status
                        task["updated_at"] = datetime.now().isoformat()
                        if self.memory_manager:
                            self.memory_manager.store("plans", active_plans)
                        logger.info(f"Updated task {task_id} status to {new_status} in plan {plan_id}")
                        result = True
                        break
                else:
                    result = False
                break
        else:
            result = False
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.log_performance_metric("update_task_status", latency)
        return result

    def log_performance_metric(self, operation: str, latency_ms: float) -> None:
        """Log performance metrics for operations to monitor latency.

        Args:
            operation: The name of the operation.
            latency_ms: The latency of the operation in milliseconds.
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "latency_ms": latency_ms
        }
        self.performance_metrics.append(metric)
        if latency_ms > 500:  # Warn if operation exceeds target latency
            logger.warning(f"High latency detected for {operation}: {latency_ms:.2f}ms")

    def create_plan(self, objective: str, context: Dict = None) -> Optional[str]:
        """Create a plan based on the given objective."""
        start_time = time.time()
        logger.debug(f"Creating plan for objective: {objective}")
        
        # Check if the result is in cache
        cache_key = f"plan_{objective}_{str(context)}"
        cached_plan_id = _plan_cache.get(cache_key)
        if cached_plan_id is not None:
            logger.info(f"Using cached plan for objective: {objective}")
            return cached_plan_id
        
        try:
            # Simulate plan creation with ethical evaluation
            plan_id = self._generate_plan_id()
            plan = {
                "id": plan_id,
                "objective": objective,
                "status": "draft",
                "tasks": []
            }
            if context:
                plan.update(context)

            # Ethical evaluation before proceeding
            ethics_context = {
                "explanation": f"Creating plan for {objective}",
                "audit_log": True,
                "bias_check": True,
                "data_protection": "user_data" not in plan or plan.get("anonymized", False),
                "user_benefit": "user_id" in plan
            }
            is_ethical, scores, explanation = self.ethics.is_action_ethical(
                f"Create plan for {objective}", ethics_context
            )
            if not is_ethical:
                logger.warning(f"Ethical violation in plan creation: {explanation}")
                return None

            # Log the ethical review
            self.ethics.log_ethical_review(
                action=f"Create plan {plan_id}",
                scores=scores,
                result="approved" if is_ethical else "rejected",
                details=explanation
            )

            self.plans[plan_id] = plan
            logger.info(f"Created plan {plan_id} for objective: {objective}")
            
            # Cache the result
            _plan_cache.set(cache_key, plan_id)
            
            return plan_id
        finally:
            latency = time.time() - start_time
            logger.info(f"Plan creation latency: {latency*1000:.2f} ms")
            if latency > 0.5:  # Warn if operation takes more than 500ms
                logger.warning(f"High latency in plan creation: {latency*1000:.2f} ms")

    def break_down_task(self, plan_id: str, task_id: str, subtasks: List[Dict]) -> bool:
        """Break down a task into subtasks."""
        start_time = time.time()
        logger.debug(f"Breaking down task {task_id} in plan {plan_id}")
        
        # Check if the result is in cache
        cache_key = f"breakdown_{plan_id}_{task_id}_{str(subtasks)}"
        cached_result = _plan_cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Using cached breakdown for task {task_id} in plan {plan_id}")
            return cached_result
        
        try:
            if plan_id not in self.plans:
                logger.error(f"Plan {plan_id} not found")
                return False

            plan = self.plans[plan_id]
            task = next((t for t in plan.get("tasks", []) if t["id"] == task_id), None)
            if not task:
                logger.error(f"Task {task_id} not found in plan {plan_id}")
                return False

            # Ethical evaluation for task breakdown
            ethics_context = {
                "explanation": f"Breaking down task {task_id} into {len(subtasks)} subtasks",
                "audit_log": True,
                "bias_check": True,
                "data_protection": "user_data" not in plan or plan.get("anonymized", False),
                "user_benefit": "user_id" in plan
            }
            is_ethical, scores, explanation = self.ethics.is_action_ethical(
                f"Break down task {task_id}", ethics_context
            )
            if not is_ethical:
                logger.warning(f"Ethical violation in task breakdown: {explanation}")
                return False

            # Log the ethical review
            self.ethics.log_ethical_review(
                action=f"Break down task {task_id}",
                scores=scores,
                result="approved" if is_ethical else "rejected",
                details=explanation
            )

            task.setdefault("subtasks", []).extend(subtasks)
            logger.info(f"Broke down task {task_id} into {len(subtasks)} subtasks")
            
            # Cache the result
            _plan_cache.set(cache_key, True)
            
            return True
        finally:
            latency = time.time() - start_time
            logger.info(f"Task breakdown latency: {latency*1000:.2f} ms")
            if latency > 0.5:  # Warn if operation takes more than 500ms
                logger.warning(f"High latency in task breakdown: {latency*1000:.2f} ms")
